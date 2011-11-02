# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Strings to be used in UI.

import gettext
from gettext import gettext as _
from gi.repository import GLib

gettext.textdomain("gmailwatcher")

# String constants
icon_name = 'gmailwatcher'

# Messages Tuple of (Title, Description)
username = GLib.get_real_name().split()[0]
username = username == 'Unknown' and GLib.get_user_name() or username

no_account = (
        _("Add an account"),
        _("Hey %s, I don't have any accounts to watch over right now."
           "Please add a gmail or google apps account and I'll let you "
           "know about any new messages.") % username
        )

quit = (
        _("ZZZzzzz..."),
        _("If you need me again, you can find me by clicking "
          "the messaging icon in the top panel.")
        )

start = (
        _("Gmail Watcher"),
        _("I'm now watching out for new mail and will stay hidden "
          "until you need me. You can find me by clicking the message icon above.")
        )

new_mail = (_("New Mail"), _("%(count)d new messages in %(folder)s"))

wrong_password = (
                _("There is a problem!"),
                _("Could not access the account %s."
                  " Please confirm that,\n"
                  "* The credentials are correct\n* IMAP is enabled in Gmail\n"
                  "* 'All Mail' folder is visible to IMAP clients\n"))
