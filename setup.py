#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name='azoufzouf',
    version='14.08',
    author='Amirouche Boubekki',
    author_email='amirouche@hypermove.net',
    description='Opinionated markup language',
    py_modules= ['azoufzouf'],
    zip_safe=False,
    license='frak it!',
    install_requires=[
        'docopt',
    ],
    entry_points={
        'console_scripts': [
            'azoufzouf = azoufzouf:main',
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
