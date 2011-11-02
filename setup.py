import os
from distutils.core import setup

from DistUtilsExtra.auto import *

data_prefix = '/data/shared'

data_files = []
for folder in os.walk(os.path.join(os.curdir, data_prefix)):
    base_folder = folder[0].split('./gmailwatcher/')[-1]
    for file in folder[-1]:
        data_files.append(os.path.join(base_folder, file))


setup(
    name='gmailwatcher',
    version='11.10.19',
    author='Owais Lone',
    author_email='hello@owaislone.org',
    description = "A desktop gmail notifier for Ubuntu OS",
    scripts=['bin/gmailwatcher'],
    packages=['gmailwatcher', 'gmailwatcher.lib', 'gmailwatcher.app'],
    package_data = {'gmailwatcher': data_files},
    data_files = [('share/indicators/messages/applications/', ['data/indicators/gmailwatcher'])],
    cmdclass={
        'build': build_extra.build_extra,
        },
    license='GNU GPLv3',
    long_description='A gmail and google apps mail notifier with instant notifications, multiple accounts and summary view.',
    classifiers=[
        'Environment :: X11 Applications :: Gnome',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Topic :: Desktop Environment :: Gnome',
        'Topic :: Communications :: Email',
        'Programming Language :: Python',
    ],

)
