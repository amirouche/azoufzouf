#!/usr/bin/env python3
"""azoufzouf.

Usage:
  azoufzouf new blog <title> <tagline> <url>
  azoufzouf new draft <title>
  azoufzouf publish [--page] <path>
  azoufzouf dung <path> [<output>]
  azoufzouf build
  azoufzouf -h | --help
  azoufzouf --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
import os
import sys
from json import loads
from json import dumps
from shutil import move
from hashlib import md5
from datetime import datetime
from docutils.core import publish_cmdline

from lxml import etree
from lxml import objectify
from docopt import docopt
from slugify import slugify

from .markup import Markup


def new_blog(**arguments):
    os.makedirs('drafts')
    with open('settings.py', 'w') as f:
        f.write('# azoufzouf settings included in all templates')
    json = dict()
    try:
        json['title'] = arguments['<title>']
    except KeyError:
        pass
    try:
        json['tagline'] = arguments['<tagline>']
    except KeyError:
        pass
    try:
        json['url'] = arguments['<url>']
    except KeyError:
        pass
    with open('settings.json', 'w') as f:
        f.write(dumps(json))
    print('Done! azoufzouf initialisation is complete.')


def new_draft(**arguments):
    title = arguments['<title>']
    slug = slugify(title)
    path = os.path.join('drafts', slug)
    if os.path.exists(path):
        print('Ark! A draft with this title already exists :/')
        sys.exit(-1)
    else:
        os.makedirs(path)
        title = len(title) * '#' + '\n' + title + '\n' + len(title) * '#' + '\n'
        index = os.path.join(path, 'index.rst')
        with open(index, 'w') as f:
            f.write(title)
    print('Done! Created draft at %s' % index)


def publish(**arguments):
    path = arguments['<path>']
    if not os.path.isdir(path):
        print('Ark! This is not a directory.') 
        sys.exit(-1)
    target = os.path.split(path)[1]
    if arguments['--page']:
        move(path, target)
    else:
        now = datetime.now()
        public = os.path.join(
            str(now.year), 
            str(now.month), 
            str(now.day),
            target,
        )
        move(path, public)
    print('Done! Published article that was found at %s', path)
    print('      It is now published at %s' % public)
    print('      Run build command to generate the website')


def build(**arguments):
    notes = dict()
    years = os.listdir()
    for year in years:
        try:
            int(year)
        except:
            continue
        else:
            notes[year] = dict()
            for month in os.listdir(year):
                path = os.path.join(year, month)
                notes[year][month] = dict()
                for day in os.listdir(path):
                    path = os.path.join(path, day)
                    notes[year][month][day] = publications = list()
                    for title in os.listdir(path):
                        path = os.path.join(path, title)
                        target = os.path.join(path, 'index.html')
                        source = os.path.join(path, 'index.rst')
                        publish_cmdline(
                            writer_name='html', 
                            argv=[source, target, '--date', '--time', '-g']
                        )
                        publish_cmdline(
                            writer_name='pdf', 
                            argv=[source, target, '--date', '--time', '-g']
                        )
                        target = dict(
                            html=target,
                            publication=datetime(year, month, day),
                        )
                        # parse html to populate ``target``
                        document = parse(target)
                        nsmap = dict(html='http://www.w3.org/1999/xhtml')
                        def lookup(xpath):
                            document.xpath(xpath, namespaces=nsmap)
                        # fuuu
                        publications.append(target)
    # check for index.jinja2

    # Ark! no jinja template, generate dummy index.html page
    with open('settings.json') as f:
        settings = loads(f.read())
    with open('index.html', 'w') as f:
        f.write('<h1>%s</h1>' % settings['title'])
        f.write('<h2>%s</h2>' % settings['tagline'])
        for year in notes.keys():
            f.write('<h3>%s</h3>' % year)
            f.write('<ul>')
            for month in notes[year]:
                for day in notes[year][month]:
                    for title in notes[year][month][day]:
                        f.write('<li><a href="%s">%s</a></li>' % (title, title))
            f.write('</ul>')


def dung(arguments):
    path = arguments['<path>']
    p = Markup.parse(path)
    json = dumps(list(p), indent=4)
    # dispatch options
    output = arguments['<output>']
    if output:
        with open(output, 'w') as f:
            f.write(json)
    else:
        print(json)


def dispatch(arguments):
    if arguments['new'] and arguments['blog']:
        new_blog(**arguments)
    if arguments['new'] and arguments['draft']:
        new_draft(**arguments)
    elif arguments['publish']:
        publish(**arguments)
    elif arguments['build']:
        build(**arguments)
    elif arguments['dung']:
        dung(arguments)
    else:
        message = 'Oops! What did happen here?! Please fill'
        message += 'a bug report with a lot of details'
        message += 'and send it at amirouche@hypermove.net'
        message += ', thanks!'
        raise Exception(message)


def main():
    arguments = docopt(__doc__, version='14.08-dev Hanging Gardens')
    dispatch(arguments)


if __name__ == '__main__':
    main()
