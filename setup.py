import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

#README = open('README.md').read()
#LICENSE = open('LICENSE.md').read()

setup(
        name="django_taskd",
        version="0.0.0a0",
        url="https://github.com/asabine/django-taskd",
        author="amelia sabine",
        author_email="amelia.sabine@getpizza.cat",
        #license=LICENSE,
        zip_safe=False,
        packages=find_packages(exclude=['tests', 'test_utils']),
        description="""A taskd implementation for the Django web framework. Enables django applications to easily integrate
        tasks with Taskwarrior.""",
        #long_description=README,
        requires=["django", "taskc"],
        classifiers=["Framework :: Django",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.5",
                  ]

    )
