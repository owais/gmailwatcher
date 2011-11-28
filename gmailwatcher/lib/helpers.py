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

import os
import sys
import json
import keyring
import gettext
from time import time as now
from gi.repository import GLib, Gio

gettext.textdomain("gmailwatcher")
_V = GLib.Variant

USER_CONFIG_DIR = GLib.get_user_config_dir()
CONFIG_DIR = "gmailwatcher"
CONFIG_FILE = "gmailwatcher.conf"
BUILDER_PATH = 'shared/ui/'
THEME_PATH = 'shared/themes/'
THEME_INDEX = 'main.html'
AUTOSTART_FILE = 'shared/autostart/gmailwatcher.desktop'
DEFAULT_FOLDERS = [(True, 'INBOX'),]
DEFAULT_LAST_CHECK = now() - 2714331  # Go one month back
DEFAULT_PREFERENCES = {
    'accounts': {},
    'preferences': {}
}
GSETTINGS_PATH = ('apps.gmailwatcher')
settings = Gio.Settings.new(GSETTINGS_PATH)


if os.path.abspath(__file__).startswith(sys.prefix):
    BASE_PATH = os.path.join(sys.prefix, 'share/gmailwatcher/')
else:
    BASE_PATH = os.path.abspath('data/')

def get_builder(builder):
    return os.path.join(BASE_PATH, BUILDER_PATH, builder)

def get_theme(theme):
    return os.path.join(BASE_PATH, THEME_PATH, theme, THEME_INDEX)

def get_desktop_file():
    base_path = BASE_PATH
    if base_path.startswith('/opt/') or base_path.startswith('/usr/'):
        return '/usr/share/applications/gmailwatcher.desktop'
    else:
        return os.path.join(
                os.path.dirname(base_path),
                'gmailwatcher.desktop'
                )

def get_password(email):
    try:
        return keyring.get_password('gmailwatcher', email) or ''
    except:
        return ''

def set_password(email, password):
    try:
        keyring.set_password('gmailwatcher', email, password)
    except:
        pass


def setup_config_dir():
    if not os.path.exists(os.path.join(USER_CONFIG_DIR, CONFIG_DIR)):
        os.mkdir(os.path.join(USER_CONFIG_DIR, CONFIG_DIR))


def save_preferences(preferences):
    '''
        Saves python dictionary as json.
    '''
    folders = {}
    display_names = {}
    last_checks = {}
    accounts = []
    for email, value in preferences['accounts'].items():
        password = value.get('password')
        set_password(email, password)
        display_names[email] = value['display_name'] or email
        folders[email] = value['folders'] or DEFAULT_FOLDERS
        last_checks_list = value['last_checks']

        for folder in folders[email]:
            last_checks_list[folder[1]] = last_checks_list.get(
                    folder[1],
                    DEFAULT_LAST_CHECK
                    )
        last_checks[email] = last_checks_list
        accounts.append(email)

    settings.delay()
    if accounts:
        settings.set_value('accounts', _V('as', accounts))
    else:
        settings.reset('accounts')

    if folders:
        settings.set_value('folders', _V('a{sa(bs)}', folders))
    else:
        settings.reset('folders')

    if display_names:
        settings.set_value('display-names', _V('a{ss}', display_names))
    else:
        settings.reset('display-names')

    if last_checks:
        settings.set_value('last-checks', _V('a{sa{sd}}', last_checks))
    else:
        settings.reset('last-checks')
    settings.apply()

def load_preferences():
    accounts = settings.get_value('accounts')
    folders = settings.get_value('folders')
    display_names = settings.get_value('display-names')
    last_checks = settings.get_value('last-checks')


    if not accounts:
        preferences = migrate_from_json()
        save_preferences(preferences)
        return preferences

    preferences = {}
    preferences.update(DEFAULT_PREFERENCES)
    for account in accounts:
        account_dict = {}
        if account in folders.keys():
            account_dict['folders'] = folders[account]
        if account in last_checks.keys():
            account_dict['last_checks'] = last_checks[account]
        if account in display_names.keys():
            account_dict['display_name'] = display_names[account]
        account_dict['password'] = get_password(account)
        preferences['accounts'][account] = account_dict
    return preferences


def migrate_from_json():
    setup_config_dir()
    try:
        config_file = open(
            os.path.join(
                USER_CONFIG_DIR,
                CONFIG_DIR,
                CONFIG_FILE
            ),
            'r'
        )
    except IOError:
        return DEFAULT_PREFERENCES

    preferences_str = config_file.read()
    config_file.close()
    try:
        preferences = json.loads(preferences_str)
    except ValueError:
        return DEFAULT_PREFERENCES

    for email, values in preferences['accounts'].items():
        password = get_password(email)
        values['password'] = password
        values['folders'] = [tuple(folder) for folder in values.get('folders', DEFAULT_FOLDERS)]
        last_checks = values.get('last_checks', {})
        for folder in values['folders']:
            last_checks[folder[1]] = last_checks.get(
                    folder[1],
                    DEFAULT_LAST_CHECK
                    )
        values['last_checks'] = last_checks
    return preferences


def set_autostart(set):
    autostart_dir = os.path.join(USER_CONFIG_DIR, "autostart")
    if not os.path.exists(autostart_dir):
        os.mkdir(autostart_dir)
    autostart_file = get_desktop_file()
    if set:
        contents = open(autostart_file).read()
        contents = contents.replace('Exec=gmailwatcher', 'Exec=gmailwatcher --quite-start')
        dest_file = os.path.join(autostart_dir, "gmailwatcher.desktop")
        dest = open(dest_file, 'w')
        dest.write(contents)
        dest.close()
    else:
        os.system('rm ' + os.path.join(autostart_dir, "gmailwatcher.desktop"))


def get_autostart():
    autostart_file = os.path.join(
            USER_CONFIG_DIR,
            "autostart",
            "gmailwatcher.desktop"
            )
    if os.path.exists(autostart_file):
        contents =  open(autostart_file, 'r').read()
        return 'X-GNOME-Autostart-enabled=false' not in contents
    else:
        return False
