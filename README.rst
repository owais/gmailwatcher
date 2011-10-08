=============
Gmail Watcher
=============


A gmail notifier for Ubuntu with support for multiple accounts and instant
notifications. It let's you subscribe to selected folders in your gmail
account and notifies about new emails immediately. 


-------------
Requirements
-------------

Please check ``debian/control`` for runtime dependencies.


-------------
Installation
-------------

Install from repository and receive automatic updates::

    sudo add-apt-repository ppa:loneowais/gmailwatcher
    sudo apt-get update
    sudo apt-get install gmailwatcher

Use ``ppa:loneowais/gmailwatcher.dev`` for development builds.

OR

Install manually from tarball::

    sudo python setup.py install --record install.record --install-layout=deb

To remove::

     sudo rm $(cat install.record)


Notes
------

* ""[Gmail]/All Main" label must be present and visible via IMAP.
  Check the labels tab in your gmail settings to confirm.

* GmailWatcher will work on any linux distro as long as the required
  packages are installed. For example, it can work on OpenSUSE as Unity is
  packaged for it.
