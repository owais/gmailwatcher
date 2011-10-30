# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2011 Owais Lone hello@owaislone.org
# This program is free software: you can redistribute it and/or modify it
# # under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
# #
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

import json
from gi.repository import WebKit

from gmailwatcher.lib.helpers import get_theme


theme_file = get_theme('dark')


class WebView(WebKit.WebView):
    def add_account(self, account, display_name, folders):
        folders = [folder for folder in folders]
        account_dict = {
            'account': account,
            'display_name': display_name,
            'folders': folders,
        }
        account_json = json.dumps(account_dict)
        js = """add_account(%s)
        """ % account_json
        self.execute_script(js)

    def new_mail(self, account, folder, thread_id, mail):
        mail_dict = {}
        mail_dict['account'] = account
        mail_dict['folder'] = folder
        mail_dict['thread_id'] = thread_id
        mail_dict['mail'] = mail
        mail_json = json.dumps(mail_dict)

        js = """new_email(%s)""" % mail_json
        self.execute_script(js)

    def show_account(self, account):
        js = 'show_account("%s");' % account
        self.execute_script(js)


def new_webview():
    webview = WebView()
    webview.set_custom_encoding('UTF-8')
    webview.open(theme_file)
    webview.show()

    return webview
