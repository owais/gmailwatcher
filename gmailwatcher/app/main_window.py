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

import time
import gettext
from gi.repository import Gtk, GObject, Notify

from gmailwatcher.app.preferences import new_preferences_dialog
from gmailwatcher.app.webview import new_webview
from gmailwatcher.app.indicator import new_application_indicator
from gmailwatcher.lib import gmail_imap as gmail_watcher
from gmailwatcher.lib.helpers import get_builder
from gmailwatcher.lib import consts


gettext.textdomain('gmailwatcher')
Notify.init('gmailwatcher')
GObject.set_prgname('ggggname')
GObject.set_application_name('Gmailwatcher')
Gtk.init([])


class MainApp:
    """
    Main class that of the applications
    Handles all the callbacks and main window UI chrome
    """
    def __init__(self, main_loop):
        self.main_loop = main_loop
        self.builder = Gtk.Builder()
        self.builder.add_from_file(get_builder('MainApp.glade'))
        self.builder.connect_signals(self)
        self.main_window = self.builder.get_object('mainwindow')
        self.about_dialog = self.builder.get_object('aboutdialog')
        self.about_dialog.connect('close', self.on_about_close)
        self.webview = new_webview()
        self.webview.connect('document-load-finished', self.setup_webkit)
        self.webview_container = self.builder.get_object('webview_container')
        self.webview_container.add(self.webview)
        self.webview_container.show()

        self.prefs = new_preferences_dialog()
        self.prefs.dialog.set_transient_for(self.main_window)
        self.watchers = {}

        self.indicator = new_application_indicator(self)

        self.finish_initialization()
        if not self.prefs.preferences['accounts']:
            self.notify(
                consts.no_account[0],
                consts.no_account[1],
                consts.icon_name
            )
            self.on_settings_clicked(self.main_window)
        else:
            self.notify(
                consts.start[0],
                consts.start[1],
                consts.icon_name
            )

    # Initializers and deployers
    def finish_initialization(self):
        """
        Initialize gmailwatcher for accounts like:
            create indicators for accounts
            setup threads for push notifications
        """
        for account, values in self.prefs.preferences['accounts'].items():
            self.indicator.add_indicator(account, values['display_name'])
        self.setup_watchers()

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

    def deploy_watcher(self, account, values):
        """
        starts a new thread for account
        """
        self.watchers[account] = w = gmail_watcher.new_watcher_thread(
            account,
            values
        )
        w.set_callback(self.new_mail)
        w.start()

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

    def check_watchers(self):
        """
        Restarts a watcher thread in case it dies for some reason
        """
        for account, watcher in self.watchers.items():
            if not watcher.isAlive():
                values = self.prefs.preferences['accounts'][account]
                self.deploy_watcher(account, values)
        return True

    def update_last_checked_time(self, account, folder):
        """
        Updates last checked date of label.
        Gmailwatcher doesn't notify about email older than last checked date
        """
        today = time.mktime(time.localtime())
        account_dict = self.prefs.preferences['accounts'][account]
        if today > account_dict['last_checks'][folder]:
            account_dict['last_checks'][folder] = today
            self.prefs.save_preferences()

    # Thread callbacks
    def new_mail(self, account, folder, new_mail):
        """
        Callback for registering new email from threads
        """
        notifications = []
        for thread_id, mail in new_mail.items():
            # Only show notif for last email in thread
            notifications.append(
                (self.prefs.preferences['accounts'][account]['display_name'],
                "%s\n%s" % (mail[-1]['from'], mail[-1]['subject']),
                "gmailwatcher")
            )
            self.update_last_checked_time(account, folder)
            self.webview.new_mail(account, folder, thread_id, mail)

        if not self.main_window.is_active():  # FIXME: Verify Behavior
            self.indicator.new_mail(account, len(new_mail))

        if len(notifications) > 2:
            self.notify(
                self.prefs.preferences['accounts'][account]['display_name'],
                consts.new_mail[1] % (len(notifications), folder),
                'gmailwatcher'
            )
        else:
            for N in notifications:
                self.notify(N[0], N[1], N[2])

    # Gtk/UI related functions
    def run(self):
        self.main_loop.run()

    def notify(self, *args):
        Notify.Notification.new(*args).show()

    def show_account(self, account):
        self.webview.show_account(account)
        self.present()

    def present(self):
        """
        Show preferences dialog if no accounts added.
        Otherwise show main app
        """
        if not self.prefs.preferences['accounts']:
            self.on_settings_clicked(self.main_window)
        if self.prefs.preferences['accounts']:
            self.main_window.present()

    #Gtk Event Callbacks
    def on_window_focus(self, widget, data=None):
        self.indicator.reset_indicators()

    def on_about_close(self, widget, data=None):
        self.about_dialog.hide()

    def on_about_clicked(self, widget, data=None):
        self.about_dialog.run()
        self.about_dialog.hide()

    def on_settings_clicked(self, widget, data=None):
        self.prefs.dialog.run()
        self.prefs.dialog.hide()
        if self.prefs.accounts_updated:
            self.update_state()
            self.prefs.accounts_updated = False

    def on_quit_clicked(self, widget, data=None):
        self.main_window.hide()
        for watcher in self.watchers.values():
            watcher.kill()
        self.main_window.destroy()

    def on_mainwindow_delete_event(self, widget, data=None):
        self.main_window.hide()
        return True

    def on_mainwindow_destroy(self, widget, data=None):
        self.main_loop.quit()
        self.notify(
            consts.quit[0],
            consts.quit[1],
            consts.icon_name
        )
