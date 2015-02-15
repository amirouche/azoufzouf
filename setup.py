#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name='azoufzouf',
    version='15.02.15',
    author='Amirouche Boubekki',
    author_email='amirouche@hypermove.net',
    description='Sleek markup language',
    py_modules=['azf'],
    zip_safe=False,
    license='frak it!',
    install_requires=[
        'docopt',
        'pygments',
        'jinja2',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
