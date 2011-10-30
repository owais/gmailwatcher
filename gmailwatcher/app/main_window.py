# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2011 Owais Lone hello@owaislone.org
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

import gettext
from gi.repository import Gtk, GObject, Notify

from gmailwatcher.app.preferences import new_preferences_dialog
from gmailwatcher.app.webview import new_webview
from gmailwatcher.app.indicator import new_application_indicator
from gmailwatcher.lib import gmail_imap as gmail_watcher
from gmailwatcher.lib.helpers import get_builder
from gmailwatcher.lib import consts

#gettext.bindtextdomain("gmailwatcher", "/usr/share/locale")
#gettext.textdomain('gmailwatcher')
Notify.init('gmailwatcher')
GObject.set_prgname('gmailwatcher')
GObject.set_application_name('Gmail Watcher')


class MainApp(object):
    """
    Main class that of the applications
    Handles all the callbacks and main window UI chrome
    """

    def __init__(self, main_loop, args=[]):
        self.main_loop = main_loop
        self.builder = Gtk.Builder()
        self.builder.add_from_file(get_builder('MainApp.glade'))
        self.builder.connect_signals(self)

        # Setup main widgets
        self.main_window = self.builder.get_object('mainwindow')
        self.about_dialog = self.builder.get_object('aboutdialog')
        self.about_dialog.connect('close', self.on_about_close)
        self.toolbar = self.builder.get_object('toolbar')
        self.accounts_list = self.builder.get_object('accounts_list')
        self.accounts_combo = self.builder.get_object('accounts_combo')

        # Setup custom progress bar style
        self.progressbar = self.builder.get_object('progressbar')
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(get_builder('css/gtk-widgets.css'))
        gtk_style = self.progressbar.get_style_context()
        gtk_style.add_provider(css_provider,  4294967295)

        # variables
        self.prefs = new_preferences_dialog()
        self.prefs.dialog.set_transient_for(self.main_window)
        self.watchers = {}
        self.progress_fractions = {}

        # Indicators
        self.indicator = new_application_indicator(self)

        # Setup webkit
        self.webview = new_webview()
        self.webview.connect('document-load-finished', self.setup_webkit)
        self.webview_container = self.builder.get_object('webview_container')
        self.webview_container.add(self.webview)
        self.webview_container.show()

        if not '--quite-start' in args:
            if not self.prefs.preferences['accounts']:
                self.notify(
                    consts.no_account[0],
                    consts.no_account[1],
                )
                self.on_preferences_clicked(self.main_window)
            else:
                self.notify(
                    consts.start[0],
                    consts.start[1],
                )
        self.finish_initialization()

    # Initializers and deployers
    def finish_initialization(self):
        """
        Initialize gmailwatcher for accounts like:
            create indicators for accounts
            setup threads for push notifications
        """
        self.accounts_list.clear()
        for account, values in self.prefs.preferences['accounts'].items():
            self.indicator.add_indicator(account, values['display_name'])
            self.progress_fractions[account] = 0.0
            self.accounts_list.append([account])
        self.setup_watchers()

    def setup_watchers(self):
        """
        Deploys threads for all accounts and adds GObject watch for them.
        GObject watch restarts a thread every 2 minutes in case something goes
        wrong like no internet connection
        """
        for account, values in self.prefs.preferences['accounts'].items():
            if not account in self.watchers:
                self.deploy_watcher(account, values)
        # FIXME: Possible better way to handle this?
        GObject.timeout_add_seconds(60 * 2, self.check_watchers)

    def deploy_watcher(self, account, values):
        """
        starts a new thread for account
        """
        self.watchers[account] = w = gmail_watcher.new_watcher_thread(
            account,
            values
        )
        w.set_callbacks({
            'mail_callback': self.new_mail,
            'progress_callback': self.update_progress,
            'wrong_password_callback': self.wrong_password
            })
        w.start()

    def update_state(self):
        """
        Called when preferences are changed while running to avoid restart.
        It kills push notification threads and restarts with new settings.
        Also cleans up indicators etc for removed accounts
        """
        self.prefs.load_preferences()
        for account, watcher in self.watchers.items():
            watcher.kill()
            self.watchers.pop(account)
        self.finish_initialization()
        self.setup_webkit()

    def setup_webkit(self, *args, **kwargs):
        """
        Sets up webkit UI for accounts, folders
        """
        for account, values in self.prefs.preferences['accounts'].items():
            folders = dict(
                (folder[1], [])
                for folder
                in values['folders']
                if folder[0])
            self.webview.add_account(account, values['display_name'], folders)

        _iter = self.accounts_list.get_iter_first()
        self.accounts_combo.set_active_iter(_iter)

    def check_watchers(self):
        """
        Restarts a watcher thread in case it dies for some reason
        """
        for account, watcher in self.watchers.items():
            if not watcher.isAlive():
                values = self.prefs.preferences['accounts'][account]
                self.deploy_watcher(account, values)
        return True

    def kill_watchers(self):
        """
        Kill all threads watching for new mail
        """
        for account, watcher in self.watchers.items():
            self.watchers.pop(account)
            watcher.kill()

    def update_last_checked_time(self, account, folder, timestamp):
        """
        Updates last checked date of label.
        Gmailwatcher doesn't notify about email older than last checked date
        """
        account_dict = self.prefs.preferences['accounts'][account]
        last_check = account_dict.get('last_checks',{}).get(folder,0.0)
        if timestamp > last_check:
            account_dict['last_checks'][folder] = timestamp
            self.prefs.save_preferences()

    def is_new(self, account, folder, mail):
        account_dict = self.prefs.preferences['accounts'][account]
        last_check = account_dict.get('last_checks',{}).get(folder,0.0)
        return mail['timestamp'] > last_check

    # Thread callbacks
    def new_mail(self, account, folder, new_mail):
        """
        Callback for registering new email from threads
        """
        notifications = []
        timestamps = []
        for thread_id, mail in new_mail.items():
            # Only show notif for last email in thread
            latest = max(mail, key=lambda M: M['timestamp'])
            timestamps.append(latest['timestamp'])
            if self.is_new(account, folder, latest):
                notifications.append(latest)

            self.webview.new_mail(account, folder, thread_id, mail)
        self.update_last_checked_time(account, folder, max(timestamps))

        if notifications:
            if not self.main_window.is_active():  # FIXME: Verify Behavior
                self.indicator.new_mail(account, len(notifications))

            if len(notifications) > 2:
                self.notify(
                    self.prefs.preferences['accounts'][account]['display_name'],
                    consts.new_mail[1] % {'count':len(notifications), 'folder':folder},
                )
            else:
                for mail in notifications:
                    notif_tuple = (
                        self.prefs.preferences['accounts'][account]['display_name'],
                        "%s\n%s" % (mail['from'], mail['subject']),
                        "gmailwatcher")
                    self.notify(notif_tuple[0], notif_tuple[1])

    def update_progress(self, account, label, fraction):
        total_fraction = 0.0
        for key, value in self.progress_fractions.items():
            total_fraction += value
        self.progress_fractions[account] = fraction
        total_fraction /= len(self.progress_fractions)
        if 0 < fraction < 1:
            self.progressbar.show()
            self.progressbar.set_fraction(total_fraction)
            self.indicator.set_progress(total_fraction)
        else:
            self.progressbar.hide()
            self.indicator.hide_progress()

    def wrong_password(self, account):
        self.notify(
                consts.wrong_password[0],
                consts.wrong_password[1] % account,
                )
        watcher = self.watchers.pop(account)
        watcher.kill()

    # Gtk/UI related functions
    def run(self):
        self.main_loop.run()

    def notify(self, title, message):
        Notify.Notification.new(
                title,
                message,
                consts.icon_name).show()

    def show_account(self, account):
        for i in self.accounts_list:
            if account == i[0]:
                self.accounts_combo.set_active_iter(i.iter)
                break
        self.webview.show_account(account)
        self.present()

    def present(self):
        """
        Show preferences dialog if no accounts added.
        Otherwise show main app
        """
        if not self.prefs.preferences['accounts']:
            self.on_preferences_clicked(self.main_window)
        if self.prefs.preferences['accounts']:
            self.main_window.present()

    #Gtk Event Callbacks
    def on_pause_switched(self, widget, data=None):
        active = widget.get_active()
        if active:
            self.setup_watchers()
        else:
            self.kill_watchers()

    def on_account_changed(self, widget, data=None):
        _iter = widget.get_active_iter()
        if _iter:
            account = self.accounts_list.get_value(_iter, 0)
            self.webview.show_account(account)

    def on_window_focus(self, widget, data=None):
        self.indicator.reset_indicators()

    def on_about_close(self, widget, data=None):
        self.about_dialog.hide()

    def on_about_clicked(self, widget, data=None):
        self.about_dialog.run()
        self.about_dialog.hide()

    def on_preferences_clicked(self, widget, data=None):
        self.prefs.dialog.run()
        self.prefs.dialog.hide()
        if self.prefs.accounts_updated:
            self.update_state()
            self.prefs.accounts_updated = False

    def on_quit_clicked(self, widget, data=None):
        self.main_window.hide()
        for watcher in self.watchers.values():
            watcher.kill()
        self.notify(
            consts.quit[0],
            consts.quit[1],
        )
        self.main_window.destroy()

    def on_mainwindow_delete_event(self, widget, data=None):
        self.main_window.hide()
        return True

    def on_mainwindow_destroy(self, widget, data=None):
        self.main_loop.quit()
