import os
from distutils.command.build import build

from django.core import management
from setuptools import find_packages, setup

from pretix_atfconsent import __version__


try:
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = ''


class CustomBuild(build):
    def run(self):
        management.call_command('compilemessages', verbosity=1)
        build.run(self)


cmdclass = {
    'build': CustomBuild
}


setup(
    name='pretix-atfconsent',
    version=__version__,
    description='A pretix plugin to collect consent from users after they have already placed their order',
    long_description=long_description,
    url='https://github.com/pc-coholic/pretix-atfconsent/',
    author='Martin Gross',
    author_email='martin@pc-coholic.de',
    license='Apache',

    install_requires=[],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretix.plugin]
pretix_atfconsent=pretix_atfconsent:PretixPluginMeta
""",
)
