# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2011 Owais Lone hello@owaislone.org
# Adapted from Cris Kirkham (http://hmmtheresanidea.blogspot.com)
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


import threading
import imaplib2
import re
import time
import codecs

from email.header import decode_header
from email.utils import parsedate_tz, formatdate, mktime_tz, parseaddr
from email import message_from_string

from gi.repository import GObject

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

class Watcher(threading.Thread):
    stop_waiting_event = threading.Event()
    seen_mail = []
    kill_now = False
    IDLE_TIMEOUT = 29  # Mins
    all_mail_folder = ''

    def __init__(self, username, password, folders, last_checks):
        self.username = username
        self.password = password
        self.folders = [F[1] for F in folders if F[0]]
        self.last_checks = last_checks
        self.last_checks_str = {}
        for folder, last_check in self.last_checks.items():
            lt = time.localtime(last_check)
            last_check_str = "%d-%s-%d" % (
                    lt.tm_mday,
                    MONTHS[lt.tm_mon-1],
                    lt.tm_year)
            self.last_checks_str[folder] = last_check_str
        threading.Thread.__init__(self)

    def run(self):
        """
        Authenticate IMAP, check for unseen mail and then wait for new mail
        """
        self.imap = imaplib2.IMAP4_SSL("imap.gmail.com")
        try:
            self.imap.login(self.username, self.password)
        except imaplib2.IMAP4_SSL.error, message:
            print 'ERROR:', message
            if 'Invalid credentials' in message:
                GObject.idle_add(self.wrong_password_callback, self.username)
            return
        self.handle_new_mail()
        self.all_mail_folder = self.get_all_mail_folder()
        while not self.kill_now:
            self.wait_for_server()

    def get_all_mail_folder(self):
        self.imap.xatom('XLIST', '', '*')
        R = self.imap.response('XLIST')[1]
        all_mail = [box for box in R if "\\AllMail" in box][0]
        return re.findall('"\[.*\].*"', all_mail)[0]

    def select_all(self):
        self.imap.select(self.all_mail_folder)


    def set_callbacks(self, cb_map):
        for name, cb in cb_map.items():
            setattr(self, name, cb)

    def decode_string(self, string):
        value, charset = decode_header(string)[0]
        try:
            return value.decode(charset or 'utf-8')
        except:
            return value

    def get_mail_headers(self, id):
        """
        Given mail ID, fetch headers along with gmail specific info
        and return in key:value form
        """
        typ, header = self.imap.uid(
            "FETCH",
            id,
            "(BODY.PEEK[HEADER.FIELDS "
            "(subject from date)] X-GM-MSGID X-GM-LABELS X-GM-THRID)"
        )
        if not header:
            return {}
        results = {}
        #parser = HeaderParser()
        #header_data = parser.parsestr(header[0][1])
        header_data = message_from_string(header[0][1])
        _from = []
        for item in parseaddr(header_data['from']):
            _from.append(self.decode_string(item))
        results['from'] = "%s <%s>" % (_from[0], _from[1])

        results['subject'] = self.decode_string(header_data['subject'])
        date = mktime_tz(parsedate_tz(header_data['date']))
        results['date'] = formatdate(date)
        results['timestamp'] = date

        match = re.search(
            'X-GM-THRID (?P<THRID>\d+) X-GM-MSGID (?P<MSGID>\d+) '
            'X-GM-LABELS \((?P<LABELS>.*)\) UID',
            header[0][0])
        results['msg_id'] = match.groupdict()['MSGID']
        results['thread_id'] = match.groupdict()['THRID']
        labels = match.groupdict()['LABELS']
        labels = re.findall('"([^"]+)"', labels)
        results['system_labels'] = [label.strip('\\\\')
                                    for label
                                    in labels
                                    if label.startswith('\\\\')]
        results['labels'] = [codecs.decode(label,'imap4-utf-7')
                             for label
                             in labels
                             if not label.startswith('\\\\')]
        if 'Starred' in results['system_labels']:
            results['system_labels'].remove('Starred')
            results['starred'] = 'starred'
        else:
            results['starred'] = ''
        return results

    def handle_new_mail(self):
        """
        Called when activity is detected on gmail server.
        Check for mail in all subscribed folders and
        send callbacks to main app with info about new mail.
        """
        for folder in self.folders:
            self.imap.select(codecs.encode(folder, 'imap4-utf-7'))
            last_check = self.last_checks_str[folder]
            typ, data = self.imap.uid(
                    'SEARCH',
                    None,
                    '(SINCE %s UNSEEN)' % last_check
                    )
            new_mail = {}  # thread_id : message
            uid_list = data[0].split()
            total = len(uid_list)
            for iterr, uid in enumerate(uid_list):
                if not uid in self.seen_mail:
                    self.seen_mail.append(uid)
                    mail_headers = self.get_mail_headers(uid)
                    if not mail_headers:
                        print 'Got empty header for uid %s' % uid
                        continue
                    thread_id = mail_headers['thread_id']
                    mail_list = new_mail.get(thread_id, [])
                    mail_list.append(mail_headers)
                    new_mail[thread_id] = mail_list
                GObject.idle_add(
                            self.progress_callback,
                            self.username,
                            folder,
                            float(iterr+1)/total
                            )
            if new_mail:
                GObject.idle_add(
                        self.mail_callback,
                        self.username,
                        folder,
                        new_mail
                        )
        self.select_all()

    def kill(self):
        self.kill_now = True  # to stop while loop in run()
        #self.imap.close()
        #self.imap.logout()
        # to let wait() to return and let execution continue
        self.stop_waiting_event.set()

    def wait_for_server(self):
        """
        Register for IDLE and check call handle_new_mail when
        activity detected in gmail
        """
        self.IDLEArgs = ''
        self.stop_waiting_event.clear()

        def _idle_callback(args):
            self.IDLEArgs = args
            self.stop_waiting_event.set()

        self.select_all()
        self.imap.idle(
            timeout=60 * self.IDLE_TIMEOUT,
            callback=_idle_callback
        )
        self.stop_waiting_event.wait()
        if not self.kill_now:
            self.handle_new_mail()
        else:
            return


def new_watcher_thread(account, values):
    watcher = Watcher(account,
                      values['password'],
                      values['folders'],
                      values['last_checks'])
    watcher.setDaemon(True)
    return watcher
