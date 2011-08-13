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
import copy
import json
import keyring
from time import time as now
from gi.repository import GLib

USER_CONFIG_DIR = GLib.get_user_config_dir()
CONFIG_DIR = "gmailwatcher"
CONFIG_FILE = "gmailwatcher.conf"
BUILDER_PATH = 'data/ui/'
THEME_PATH = 'data/themes/'
THEME_INDEX = 'main.html'
DEFAULT_LAST_CHECK = now() - 2714331 # Go one month back
DEFAULT_preferences = {
    'accounts': {},
    'preferences': {
        'autostart':True,
    }
}


def get_base_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_builder(builder):
    return os.path.join(get_base_path(), BUILDER_PATH, builder)
    

def get_theme(theme):
    return os.path.join(get_base_path(), THEME_PATH, theme, THEME_INDEX)


def get_desktop_file():
    base_path = get_base_path()
    if base_path.startswith('/opt/owaislone/'):
        return '/usr/share/applications/gmailwatcher.desktop'
    else:
        return os.path.join(os.path.dirname(base_path), 'gmailwatcher.desktop') 

def get_password(email):
    return keyring.get_password('gmailwatcher', email) or ''

def set_password(email, password):
    keyring.set_password('gmailwatcher', email, password)


def save_preferences(preferences):
    '''
        Saves python dictionary as json.
    '''
    _preferences = copy.deepcopy(preferences)
    for email, value in _preferences['accounts'].items():
        password = value.pop('password')
        set_password(email, password)
    preferences_str = json.dumps(_preferences)
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
        last_checks = values.get('last_checks',{})
        for folder in values['folders']:
            last_checks[folder[1]] = last_checks.get(folder[1], DEFAULT_LAST_CHECK)
        values['last_checks'] = last_checks
    return preferences


def set_autostart(set):
    autostart_dir = os.path.join(USER_CONFIG_DIR, "autostart")
    if not os.path.exists(autostart_dir):
        os.mkdir(autostart_dir)
    autostart_file = get_desktop_file()
    if set:
        file = open(autostart_file)
        source = file.read()
        file.close()
        dest_file = os.path.join(autostart_dir, "gmailwatcher.desktop")
        dest = open(dest_file,'w')
        dest.write(source)
        dest.close()
    else:
        os.system('rm ' + os.path.join(autostart_dir, "gmailwatcher.desktop"))

def get_autostart():
    autostart_file = os.path.join(USER_CONFIG_DIR, "autostart", "gmailwatcher.desktop")
    if os.path.exists(autostart_file):
        return True
    else:
        return False
