#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name='azoufzouf',
    version='14.08-dev',
    author='Amirouche Boubekki',
    author_email='amirouche@hypermove.net',
    description='Opinionated markup language',
    packages = ['azoufzouf'],
    zip_safe=False,
    license='AGPL',
    install_requires=[
        'docopt',
        'unicode-slugify',
    ],
    entry_points={
        'console_scripts': [
            'azoufzouf = azoufzouf.main:main',
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
