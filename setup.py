import os
import site
from distutils.core import setup

from DistUtilsExtra.auto import *

data_prefix = 'gmailwatcher/data/'

data_files = []
for folder in os.walk(os.path.join(os.curdir, data_prefix)):
    base_folder = folder[0].split('./gmailwatcher/')[-1]
    for file in folder[-1]:
        data_files.append(os.path.join(base_folder, file))

site.addsitedir('/opt/owaislone/')

setup(
    name='gmailwatcher',
    version='11.10',
    author='Owais Lone',
    author_email='hello@owaislone.org',
    scripts=['bin/gmailwatcher'],
    packages=['gmailwatcher', 'gmailwatcher.lib', 'gmailwatcher.app'],
    package_data = {'gmailwatcher': data_files},
    #data_files=[('/usr/share/indicators/messages/applications', ['%sindicators/gmailwatcher' % data_prefix])],
    cmdclass={
        'build': build_extra.build_extra,
        #'build_icons': build_icons.build_icons,
        #'build_i18n': build_i18n.build_i18n,
        },
    license='GNU GPLv3',
    long_description='long long long description',
)
