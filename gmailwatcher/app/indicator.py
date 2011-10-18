# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2011 Owais Lone hello@owaislone.org
# This program is free software: you can redistribute it and/or modify it
# # under the terms of the GNU General Public License version 3, as published
# # by the Free Software Foundation.
# #
# This program is distributed in the hope that it will be useful, but
# # WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# # PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

from gi.repository import Indicate, Unity
#from gettext import gettext as _

from gmailwatcher.lib.helpers import get_desktop_file


desktop_file = get_desktop_file()


class Indicator:
    def __init__(self):
        self.launcher_entry = Unity.LauncherEntry.get_for_desktop_file(
                desktop_file)
        self.server = Indicate.Server.ref_default()
        self.server.set_dbus_object('/org/owaislone/gmailwatcher')
        self.server.set_desktop_file(desktop_file)
        self.server.set_type("message.mail")
        self.server.connect("server-display", self.clicked_server)
        self.server.show()
        self.indicators = {}
        self.count = 0

    def add_indicator(self, account, display_name):
        if not account in self.indicators.keys():
            indicator = Indicate.Indicator()
            indicator.set_property("subtype", "mail")
            indicator.set_property("name", display_name)
            indicator.connect("user-display", self.clicked_indicator, account)
            self.indicators[account] = indicator
            self.server.add_indicator(indicator)

    def new_mail(self, account, count):
        indicator = self.indicators[account]
        self.count += count
        indicator.set_property('count', str(self.count))
        indicator.set_property('draw-attention', 'true')
        indicator.show()
        self.launcher_entry.set_property('count', self.count)
        self.launcher_entry.set_property('count-visible', True)
        self.launcher_entry.set_property("urgent", True)

    def reset_indicators(self):
        self.count = 0
        for indicator in self.indicators.values():
            indicator.set_property('draw-attention', 'false')
            indicator.set_property('count', '0')
            indicator.hide()
        self.launcher_entry.set_property('count', 0)
        self.launcher_entry.set_property('count-visible', False)
        self.launcher_entry.set_property("urgent", False)

    def set_progress(self, fraction):
        self.launcher_entry.set_property('progress', fraction)
        self.launcher_entry.set_property('progress-visible', True)

    def hide_progress(self):
        self.launcher_entry.set_property('progress-visible', False)

    def clicked_server(self, widget, data=None):
        self.main_app.present()

    def clicked_indicator(self, indicator, signal, account):
        self.main_app.show_account(account)


def new_application_indicator(main_app):
    ind = Indicator()
    ind.main_app = main_app
    return ind
