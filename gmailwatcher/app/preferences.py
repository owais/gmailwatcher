# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2011 Owais Lone hello@owaislone.org
# This program is free software: you can redistribute it and/or modify it
# # under the terms of the GNU General Public License version 3, as published
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

import re
import codecs
import threading
import gettext
from gettext import gettext as _
from gi.repository import Gtk, GObject

from gmailwatcher.lib import imaplib2
from gmailwatcher.lib.helpers import (save_preferences,
                                      load_preferences,
                                      get_builder,
                                      set_autostart,
                                      get_autostart)

gettext.textdomain("gmailwatcher")
ENTRY_ICON_POS = Gtk.EntryIconPosition.SECONDARY


class PreferencesDialog(object):
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(get_builder('Preferences.glade'))
        self.builder.connect_signals(self)
        self.dialog = self.builder.get_object('PreferencesDialog')

        #Get Widgets
        self.account_form = self.builder.get_object('AccountForm')
        self.accounts_treeview = self.builder.get_object('accounts_treeview')
        self.autostart_switch = self.builder.get_object('autostart_switch')
        self.save_button = self.builder.get_object('save_button')
        self.load_folders_button = self.builder.get_object('load_folders')
        self.load_folders_label = self.load_folders_button.get_label()

        #Get Form Elements
        self.email_form = self.builder.get_object('email_form')
        self.password_form = self.builder.get_object('password_form')
        self.display_name_form = self.builder.get_object('display_name_form')

        #ListStores
        self.folder_store = self.builder.get_object('folder_store')
        self.account_store = self.builder.get_object('account_store')

        self.accounts_updated = False
        self.preferences = {}
        self.load_preferences()
        self.threads = []

    def show(self):
        self.dialog.show()

    def reset_load_folders_button(self, label=None):
        self.load_folders_button.set_label(label or self.load_folders_label)
        self.load_folders_button.set_sensitive(True)

    def validate_email(self, widget=None, data=None):
        email = self.email_form.get_text()
        if re.match('.+@.+[.].+', email):
            self.email_form.set_icon_from_stock(ENTRY_ICON_POS, None)
            return True
        else:
            self.email_form.set_icon_from_stock(ENTRY_ICON_POS,
                    Gtk.STOCK_DIALOG_WARNING)
            return False

    def validate_password(self, widget=None, data=None):
        password = self.password_form.get_text()
        if password:
            self.password_form.set_icon_from_stock(ENTRY_ICON_POS, None)
            return True
        else:
            self.password_form.set_icon_from_stock(ENTRY_ICON_POS,
                    Gtk.STOCK_DIALOG_WARNING)
            return False

    def validate_folders(self, widget=None, data=None):
        for i in self.folder_store:
            if i[0]:
                return True
        return False

    def validate_form(self, widget=None, data=None):
        valid = False not in [self.validate_password(), self.validate_email(),
                 self.validate_folders()]
        self.save_button.set_sensitive(valid)
        return valid

    def get_mail_folders(self):
        email = self.email_form.get_text()
        password = self.password_form.get_text()
        try:
            M = imaplib2.IMAP4_SSL("imap.gmail.com")
            response = M.login(email, password)
        except imaplib2.IMAP4_SSL.error:
            GObject.idle_add(self.reset_load_folders_button, _('Failed.. Try Again'))
            return
        GObject.idle_add(self.reset_load_folders_button)
        if response[0] == 'OK':
            folders = M.list()
            regex = re.compile(r'\(.*? ".*" "(?P<mailbox>.*)"')
            folder_list = [row[0] for row in self.folder_store]
            for folder in folders[1]:
                if not '\Noselect' in folder:
                    mailbox = regex.match(folder).groups()[0]
                    mailbox = codecs.decode(mailbox, 'imap4-utf-7')
                    folder_list = [row[1] for row in self.folder_store]
                    if not mailbox in folder_list:
                        self.folder_store.append([False, mailbox])
        M.logout()

    def save_account(self, account):
        accounts = self.preferences.get('accounts', {})
        accounts[self.email_form.get_text()] = account
        self.preferences['accounts'] = accounts
        self.save_preferences()
        self.load_preferences()
        self.accounts_updated = True

    def save_preferences(self):
        save_preferences(self.preferences)

    def load_preferences(self):
        self.preferences = load_preferences()
        self.account_store.clear()
        for account in self.preferences['accounts'].keys():
            self.account_store.append([account])
        autostart = get_autostart()
        self.autostart_switch.set_active(autostart)

    def reset_account_form(self):
        self.email_form.set_text('')
        self.password_form.set_text('')
        self.display_name_form.set_text('')
        self.folder_store.clear()

    #Signals
    def on_folder_toggled(self, widget, index):
        self.folder_store[index][0] = not self.folder_store[index][0]
        self.validate_form()

    def on_load_folders_clicked(self, widget, data=None):
        self.load_folders_button.set_label(_('Loading...'))
        self.load_folders_button.set_sensitive(False)
        get_folders_thread = threading.Thread(target=self.get_mail_folders)
        get_folders_thread.setDaemon(True)
        get_folders_thread.start()

    def on_account_selected(self, widget, data=None):
        self.reset_load_folders_button()
        selection = widget.get_selection()
        model, iter = selection.get_selected()
        if iter:
            email = model.get_value(iter, 0)
            account = self.preferences['accounts'][email]
            self.email_form.set_text(email)
            self.password_form.set_text(account['password'])
            self.display_name_form.set_text(account['display_name'])
            self.folder_store.clear()
            if account['folders']:
                self.save_button.set_sensitive(True)
            for folder in account['folders']:
                self.folder_store.append([folder[0], folder[1]])
            self.account_form.show()
        self.validate_form()

    def on_account_add(self, widget, data=None):
        self.reset_load_folders_button()
        self.save_button.set_sensitive(False)
        self.reset_account_form()
        self.account_form.show()

    def on_account_save(self, widget, data=None):
        if self.validate_form():
            account = {
                'password': self.password_form.get_text(),
                'display_name': self.display_name_form.get_text(),
                'folders': [(folder[0], folder[1])
                            for folder
                            in self.folder_store]
            }
            self.save_account(account)
            email = self.email_form.get_text()
            if not email in [row[0] for row in self.account_store]:
                self.account_store.append([self.email_form.get_text()])
            self.account_form.hide()
        self.save_button.set_sensitive(False)

    def on_account_delete(self, widget, data=None):
        selection = self.accounts_treeview.get_selection()
        model, iter = selection.get_selected()
        if iter:
            email = model.get_value(iter, 0)
            self.preferences['accounts'].pop(email)
            self.account_store.remove(iter)
            self.account_form.hide()
            self.reset_account_form()
            self.save_preferences()

    def on_autostart_toggled(self, widget, active):
        set_autostart(widget.get_active())


    def on_delete(self, widget, data=None):
        self.dialog.hide()
        return True


def new_preferences_dialog():
    return PreferencesDialog()
