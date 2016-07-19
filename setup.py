import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

#README = open('README.md').read()
#LICENSE = open('LICENSE.md').read()

setup(
        name="django-taskd",
        version="0.0.0-alpha",
        url="https://github.com/asabine/django-taskd",
        author="amelia sabine",
        author_email="amelia.sabine@getpizza.cat",
        #license=LICENSE,
        zip_safe=False,
        py_modules=['taskdj'],
        description="""A taskd implementation for the Django web framework. Enables django applications to easily integrate
        tasks with Taskwarrior.""",
        #long_description=README,
        requires=["django", "taskc"],
        classifiers=["Framework :: Django",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.5",
                  ]

    )
