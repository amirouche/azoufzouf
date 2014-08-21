#! /usr/bin/env python3

# Copyright © 2014 Amirouche Boubekki <amirouche@hypermove.net>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Frak It To Public License, Version 14.08 or later.
#
#
#                    FRAK IT TO PUBLIC LICENSE
#                          Version 14.08

# Copyright (C) 2014 Amirouche Boubekki <amirouche@hypermove.net>

# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.

#                    FRAK IT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

#  0. Do what the FRAK you can do.
#  1. Do FRAK what the FRAK you can do
#  3. Do FRAK what the FRAK you can FRAK do
"""azoufzouf.

Usage:
  azoufzouf <path> [<output>]
  azoufzouf -h | --help
  azoufzouf --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
import os
import sys
from json import dumps

from docopt import docopt


class Markup:

    @classmethod
    def parse(cls, file):
        with open(file) as f:
            string = f.read()
        return cls(string)

    def __init__(self, string):
        self.source = string
        self.context = dict()
        self.position = 0
        self.context = dict()

    def has_next(self):
        return self.position < len(self.source)

    def next(self):
        if self.position > len(self.source):
            raise StopIteration
        else:
            self.position += 1
            if self.position == len(self.source):
                raise StopIteration
            else:
                try:
                    return self.source[self.position]
                except IndexError:
                    raise StopIteration

    def peek(self, relative=0):
        return self.source[self.position + relative]

    def __iter__(self):
        next = self.peek()
        while True:
            if next == 'ⵣ':
                command = self._command()
                if command['name'] == 'set':
                    # update context
                    key = command['argument'][1:-1]
                    value = command['text']
                    self.context[key] = value
                    # recurse to find something that is not a ``set`` command
                    yield from self.__iter__()
                else:
                    try:
                        argument = command['argument']
                    except KeyError:
                        pass
                    else:
                        if argument[0] != '"':
                            # argument is not a string, retrieve value
                            # in context
                            argument = self.context[argument]
                            command['argument'] = argument
                    finally:
                        yield command
            else:
                yield self._text()
            try:
                next = self.peek()
            except IndexError:
                raise StopIteration

    def _command(self):
        output = dict(kind='command')
        name = self._command_name()
        output['name'] = name
        try:
            argument = self._command_argument()
        except Exception as e:
            pass
        else:
            output['argument'] = argument
        try:
            text = self._command_text()
        except Exception as e:
            pass
        else:
            output['text'] = text
        return output

    def _command_name(self):
        name = ''
        while True:
            next = self.next()
            if next.isalpha():
                name += next
            else:
                return name

    def _command_argument(self):
        if self.peek() != '[':
            raise Exception('no arguments')
        argument = self.next()
        while True:
            next = self.next()
            if next != ']':
                argument += next
            else:
                self.next()  # consume closing bracket
                return argument

    def _command_text(self):
        next = self.peek()
        if next != '{':
            raise Exception('no text')
        else:
            text = ''
            next = self.next()
            while True:
                if next == '}':
                    self.next()  # consume closing bracket
                    return text
                else:
                    text += next
                    next = self.next()

    def _text(self):
        output = self.peek()
        next = self.next()
        while True:
            if next == 'ⵣ' and self.peek(1) == 'ⵣ':
                output += next
                self.next()  # consume escape char
                next = self.next()
            elif next == 'ⵣ':
                return dict(kind='text', value=output)
            else:
                output += next
                try:
                    next = self.next()
                except StopIteration:
                    return dict(kind='text', value=output)


def dung(arguments):
    path = arguments['<path>']
    markup = Markup.parse(path)
    json = dumps(list(markup), indent=4)
    # dispatch options
    output = arguments['<output>']
    if output:
        with open(output, 'w') as f:
            f.write(json)
    else:
        print(json)

def dispatch(arguments):
    if arguments['<path>']:
        dung(arguments)
    else:
        message = 'Oops! What did happen here?! Please fill '
        message += 'a bug report with a lot of details using DEBUG=FIXME '
        message += 'and send output at amirouche@hypermove.net'
        message += ', thanks!'
        raise Exception(message)


def main():
    arguments = docopt(__doc__, version='14.08-dev Hanging Gardens')
    if os.environ.get('DEBUG', False):
        print(arguments)
    dispatch(arguments)


if __name__ == '__main__':
    main()
