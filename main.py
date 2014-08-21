#!/usr/bin/env python3
"""main.py.

Usage:
  main.py build
  main.py -h | --help
  main.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
import os
from xml.sax.saxutils import escape
from subprocess import check_output

from docopt import docopt
from markupsafe import escape

from azoufzouf import Markup


class HTMLDocBuilder:

    def __init__(self):
        self.last = None

    def build(self, arguments):
        # command calls are translated to method calls
        self.output = ''
        dungs = Markup.parse('index.azf')
        for dung in dungs:
            from pprint import pprint
            print(dung)
            if dung['kind'] == 'command':
                name = dung['name']
                method = getattr(self, name)
                argument = dung.get('argument', None)
                text = dung.get('text', None)
                output = method(argument, text)
                self.output += output
            else:
                text = dung['value']
                if text.isspace():
                    self.last = text
                    continue
                if self.last and self.last.endswith('\n\n'):
                    self.output += '</p>'
                    self.output += '<p class="main paper">'
                if not self.last:
                    self.output += '<p class="main paper">'
                self.output += '%s' % text
                self.last = text
        with open('index.html.template', 'r') as f:
            template = f.read()
        self.output = template.replace('{{ MAIN }}', self.output)
        with open('index.html', 'w') as f:
            f.write(self.output)

    def help(self, *ignored):
        if self.last:
            self.output += '</p>'
        self.last = None
        output = check_output(["azoufzouf", "--help"])
        output = output.decode('utf-8')
        output = escape(output)
        return '<pre class="main paper">%s</pre>' % output

    def section(self, argument, text):
        if self.last:
            self.output += '</p>'
        self.last = None
        return '<h1 class="main paper">%s</h1>' % text

    def href(self, argument, text):
        self.last = None
        self.last = 'not-ending-with-two-carriage-return'
        return '<a href="%s">%s</a>' % (argument, text)

    def code(self, ignored, text):
        self.last = 'not-ending-with-two-carriage-return'
        return '<code>%s</code>' % text

    def include(self, file, ignore):
        if self.last:
            self.output += '</p>'
        self.last = None
        file = file[1:-1]
        with open(file) as f:
            output = f.read()
        output = escape(output)
        return '<pre class="main paper">%s</pre>' % output

    def python(self, file, ignored):
        if self.last:
            self.output += '</p>'
        self.last = None
        file = file[1:-1]
        #file = os.path.abspath(file)
        command = 'pygmentize -f html %s' % file
        output = check_output(command.split())
        output = output.decode('utf-8')
        return '<div class="main paper">%s</div>' % output
        
        

def dispatch(arguments):
    if arguments['build']:
        HTMLDocBuilder().build(arguments)
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
