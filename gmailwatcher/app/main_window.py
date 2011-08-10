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

from gi.repository import Gtk, GObject, Notify

from gmailwatcher.app.preferences import new_preferences_dialog
from gmailwatcher.app.webview import new_webview
from gmailwatcher.app.indicator import new_application_indicator
from gmailwatcher.lib import gmail_imap as gmail_watcher
from gmailwatcher.lib.helpers import get_builder


class MainApp:
    def __init__(self, main_loop):
        Notify.init('gmailwatcher')

        self.main_loop = main_loop
        self.builder = Gtk.Builder()
        self.builder.add_from_file(get_builder('MainApp.glade'))
        self.builder.connect_signals(self)
        self.main_window = self.builder.get_object('mainwindow')
        self.about_dialog = self.builder.get_object('aboutdialog')
        self.about_dialog.connect('close',self.on_about_close)
        self.webview = new_webview()
        self.webview.connect('document-load-finished', self.setup_webkit)
        self.webview_container = self.builder.get_object('webview_container')
        self.webview_container.add(self.webview)
        self.webview_container.show()

        self.prefs = new_preferences_dialog()
        self.prefs.dialog.set_transient_for(self.main_window)
        self.mails = {}
        self.watchers = {}

        self.indicator = new_application_indicator(self)  

        self.finish_initialization()
        if not self.prefs.preferences['accounts']:
            self.on_settings_clicked(self.main_window)

    def finish_initialization(self):
        for account, values in self.prefs.preferences['accounts'].items():
            self.mails[account] = {}
            self.mails[account] = dict(
                (folder[1], [])
                for folder
                in values['folders']
                if folder[0]
            )
            self.indicator.add_indicator(account, values['display_name'])
        self.setup_watchers()

    def update_state(self):
        for account, watcher in self.watchers.items():
            watcher.kill()
            self.watchers.pop(account)
        self.finish_initialization()
        self.setup_webkit()

    def deploy_watcher(self, account, values):
        self.watchers[account] = w= gmail_watcher.new_watcher_thread(
            account,
            values
        )
        w.set_callback(self.new_mail)
        w.start()

    def setup_watchers(self):
        for account, values in self.prefs.preferences['accounts'].items():
            if not account in self.watchers:
                self.deploy_watcher(account, values)
        GObject.timeout_add_seconds(60*2, self.check_watchers)

    def check_watchers(self):
        for account, watcher in self.watchers.items():
            if not watcher.isAlive():
                values= self.prefs.preferences['accounts'][account]
                self.deploy_watcher(account, values)
        return True

    def setup_webkit(self, *args, **kwargs):
        for account, values in self.prefs.preferences['accounts'].items():
            folders = dict(
                (folder[1], [])
                for folder
                in values['folders']
                if folder[0])
            self.webview.add_account(account, values['display_name'], folders)

    def run(self):
        self.main_loop.run()

    def new_mail(self, account, folder, new_mail):
        notifications = []
        for thread_id, mail in new_mail.items():
            # Only show notif for last email in thread
            notifications.append(
                (account,
                "%s\n%s" % (mail[-1]['from'], mail[-1]['subject']),
                "gmailwatcher")
            )
            self.set_last_checked_time(account, mail[-1]['time'])
            self.webview.new_mail(account, folder, thread_id, mail)

        if not self.main_window.is_active():  #FIXME: Verify Behavior
            self.indicator.new_mail(account, len(new_mail))

        if len(notifications) > 2:
            self.notify(
                account, 
                '%d new emails in %s' % (len(notifications), folder),
                'gmailwatcher'
            )
        else:
            for N in notifications:
                self.notify(N[0], N[1], N[2])

    def notify(self, *args):
        Notify.Notification.new(*args).show()

    def set_last_checked_time(self, account, time):
        if time > self.prefs.preferences['accounts'][account]['last_checked']:
            self.prefs.preferences['accounts'][account]['last_checked'] = time
            self.prefs.save_preferences()

    def show_account(self, account):
        self.webview.show_account(account)
        self.present()

    def present(self):
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
        self.update_state()

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
