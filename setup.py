#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from distutils.core import Command


class TestCommand(Command):
    user_options = []
    package = 'memento'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        settings.configure(
            DATABASES={
                'default': {
                    'NAME': ':memory:',
                    'ENGINE': 'django.db.backends.sqlite3'
                }
            },
            INSTALLED_APPS=(self.package,),
            MIDDLEWARE_CLASSES=()
        )
        from django.core.management import call_command
        import django
        if django.VERSION[:2] >= (1, 7):
            django.setup()
        call_command('test', self.package)


setup(
    name='django-memento-framework',
    version='0.0.3',
    description='A set for helpers for Django web sites to enable the \
Memento framework for time-based access',
    author='Ben Welsh',
    author_email='ben.welsh@gmail.com',
    url='http://django-memento-framework.readthedocs.org',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,  # because we're including static files
    install_requires=(
        'python-dateutil',
    ),
    cmdclass={'test': TestCommand}
)