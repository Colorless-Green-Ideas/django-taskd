import os
from setuptools import setup

README = open('README.md').read()
LICENSE = open('LICENSE.txt').read()

setup(
        name="django-taskd",
        version="0.0.0-alpha"
        url="https://github.com/asabine/django-taskd",
        author="amelia sabine",
        author_email="amelia.sabine@getpizza.cat"
        license=LICENSE,
        py_modules=['taskdj']
        description="""A taskd implementation for the Django web framework. Enables django applications to easily integrate
        tasks with Taskwarrior."""
        long_description=README,
        install_requires=['django', 'taskc'],
    )
