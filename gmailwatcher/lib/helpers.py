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
import copy
import json
import keyring
import gettext
from time import time as now
from gi.repository import GLib

gettext.textdomain("gmailwatcher")


USER_CONFIG_DIR = GLib.get_user_config_dir()
CONFIG_DIR = "gmailwatcher"
CONFIG_FILE = "gmailwatcher.conf"
BUILDER_PATH = 'shared/ui/'
THEME_PATH = 'shared/themes/'
THEME_INDEX = 'main.html'
AUTOSTART_FILE = 'shared/autostart/gmailwatcher.desktop'
DEFAULT_FOLDERS = [[True, 'INBOX'],]
DEFAULT_LAST_CHECK = now() - 2714331  # Go one month back
DEFAULT_preferences = {
    'accounts': {},
    'preferences': {}
}


def get_base_path():
    current_path = os.path.abspath(__file__)
    if current_path.startswith(sys.prefix):
        return os.path.join(sys.prefix, 'share/gmailwatcher/')
    else:
        return os.path.abspath('data/')

def get_builder(builder):
    return os.path.join(get_base_path(), BUILDER_PATH, builder)

def get_theme(theme):
    return os.path.join(get_base_path(), THEME_PATH, theme, THEME_INDEX)

def get_desktop_file():
    base_path = get_base_path()
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
    setup_config_dir()
    _preferences = copy.deepcopy(preferences)
    for email, value in _preferences['accounts'].items():
        password = value.pop('password')
        set_password(email, password)
        value['display_name'] = value['display_name'] or email
        value['folders'] = value['folders'] or DEFAULT_FOLDERS
    preferences_str = json.dumps(_preferences, indent=2)
    config_file = open(
        os.path.join(
            USER_CONFIG_DIR,
            CONFIG_DIR,
            CONFIG_FILE
        ),
        'w'
    )
    config_file.write(preferences_str)
    config_file.close()


def load_preferences():
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
        return DEFAULT_preferences

    preferences_str = config_file.read()
    config_file.close()
    try:
        preferences = json.loads(preferences_str)
    except ValueError:
        return DEFAULT_preferences

    for email, values in preferences['accounts'].items():
        password = get_password(email)
        values['password'] = password
        values['folders'] = values.get('folders', DEFAULT_FOLDERS)
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
        file = open(autostart_file)
        source = file.readlines()
        file.close()
        source = [line.strip() for line in source]
        exec_index = source.index('Exec=gmailwatcher')
        source[exec_index] ='Exec=gmailwatcher --quite-start'
        source = '\n'.join(source)
        dest_file = os.path.join(autostart_dir, "gmailwatcher.desktop")
        dest = open(dest_file, 'w')
        dest.write(source)
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
        lines = [line.strip() for line in open(autostart_file, 'r').readlines()]
        for line in lines:
            if line.startswith('X-GNOME-Autostart-enabled='):
                if line.split('=')[1].strip() == 'true':
                    return True
                else:
                    return False
        return True
    else:
        return False
