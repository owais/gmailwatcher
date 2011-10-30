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

    sudo add-apt-repository ppa:loneowais/gmailwatcher.dev
    sudo apt-get update
    sudo apt-get install gmailwatcher

OR

Install manually from tarball::

    sudo python setup.py install --record install.record --install-layout=deb

To remove::

     sudo rm $(cat install.record)


Notes
------

* "[Gmail]/All Mail" label must be present and visible via IMAP.
  Check the labels tab in your gmail settings to confirm.

* To run directly from source:
    
    >>> bin/gmailwatcher
