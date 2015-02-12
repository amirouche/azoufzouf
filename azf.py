#!/usr/bin/env python3
import os

from html import escape
from functools import wraps
from contextlib import contextmanager

from docopt import docopt
from jinja2 import Environment
from jinja2 import FileSystemLoader

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name
from pygments.util import ClassNotFound


class EndOfFile(Exception):
    pass


class AzoufzoufException(Exception):
    pass


class StringNavigator(object):

    def __init__(self, source):
        self.position = -1
        self.source = source

    def next(self):
        self.position += 1
        try:
            return self.source[self.position]
        except IndexError:
            raise EndOfFile

    def back(self):
        self.position -= 1

    def takewhile(self, predicate):
        out = ''
        while True:
            try:
                char = self.next()
            except EndOfFile:
                return out, EndOfFile
            else:
                if predicate(char):
                    out += char
                else:
                    return out, char


def parse(source, command_character="ⵣ"):
    source = StringNavigator(source)
    eol_count = 1
    while True:
        text, why = source.takewhile(lambda char: char not in (command_character, '\n'))

        if why is EndOfFile and text:
            yield dict(kind='text', value=text)
            raise StopIteration

        elif why is EndOfFile:
            raise StopIteration

        elif why == '\n' and text:
            yield dict(kind='text', value=text)
            yield dict(kind='eol')

        elif why == '\n':
            yield dict(kind='eol')

        elif why == command_character:
            if text:
                yield dict(kind='text', value=text)

            name, why = source.takewhile(lambda char: char not in ('{', ' ', '\n', command_character))
            if why in ('\n', ' ', command_character, EndOfFile):
                yield dict(kind='command', value=name, arguments=tuple())
                if why is EndOfFile:
                    raise StopIteration
                else:
                    # avoid consuming the next value's first char
                    source.back()
                    continue

            else:  # met a curly brace, parse arguments
                nesting_level = 1
                arguments = list()
                argument = ''
                while True:
                    # parse one argument
                    content, why = source.takewhile(lambda char: char not in ('{', '}'))
                    if why is '{':
                        nesting_level += 1
                        argument += content + why
                    elif why == '}' and (nesting_level - 1) > 0:
                        nesting_level -= 1
                        argument += content + why
                    else:
                        argument += content
                        argument = list(parse(argument, command_character))
                        arguments.append(argument)
                        try:
                            next = source.next()
                        except EndOfFile:
                            yield dict(kind='command', value=name, arguments=arguments)
                            raise StopIteration
                        if next == '{':
                            nesting_level = 1
                            argument = ''
                            # there is at least one more arguments to parse
                            continue
                        else:
                            # End of command, there is more text to parse,
                            # avoid consuming the next value's first char.
                            source.back()
                            yield dict(kind='command', value=name, arguments=arguments)
                            break

        else:
            msg = 'Not sure what happened, you should ask a hearing to the king...'
            raise AzoufzoufException(mg)


def is_paragraph(func):
    """Declare a command a paragraph to avoid wrapping it in <p> tags"""
    func.is_paragraph = True
    return func



NOMODE, PARAGRAPH, INLINE, VERBATIM = range(4)

def compose(*funcs):
    def composed(*args):
        out = funcs[0](*args)
        for func in funcs[1:]:
            out = func(out)
        return out
    return composed


pygments_html_formatter = get_formatter_by_name('html')


class HTMLRender:

    is_paragraph = is_paragraph

    def __call__(self, source, context, basepath):
        self._context = dict(**context)
        self._basepath = basepath

        self._mode = NOMODE   # add link
        self._space_count = 0

        body = ''.join(self.render(source))
        self._context['body'] = body

        return self._context

    def _emit(self, value):

        if value == ' ' and self._mode != INLINE:
            self._space_count += 1
        elif value == '\n':
            self._space_count = 0
            if self._mode == PARAGRAPH:
                yield '</p>'
                self._mode = NOMODE
            elif self._mode == VERBATIM:
                yield '\n'
        else:
            if self._space_count == 1 and self._mode in (PARAGRAPH, INLINE):
                yield ' '
            if self._mode == NOMODE:
                self._mode = PARAGRAPH
                yield '<p>'
            yield from value
          
    @contextmanager
    def _inline(self):
        previous = self._mode
        self._mode = INLINE
        yield
        self._mode = previous

    @contextmanager
    def _verbatim(self):
        previous = self._inline
        self._mode = VERBATIM
        yield
        self._mode = previous

    def render(self, items):
        """Takes the output of azf.render and yields html strings"""
        eol_count = 0
        for item in items:
            kind = item['kind']
            if kind == 'command':
                eol_count = 0
                command = item['value']
                try:
                    method = getattr(self, command)
                except AttributeError:
                    raise AzoufzoufException('Unknown command: %s' % command)
                else:
                    if getattr(method, 'is_paragraph', False):
                        with self._inline():
                            yield from method(*item['arguments'])
                    else:
                        yield from method(*item['arguments'])
            elif kind == 'text':
                eol_count = 0
                yield from self._emit(item['value'])
            elif kind == 'eol' and self._mode == VERBATIM:
                yield from self._emit('\n')
            elif kind == 'eol' and eol_count == 1:
                yield from self._emit('\n')
            elif kind == 'eol':
                eol_count += 1
                yield from self._emit(' ')
            else:
                msg = 'Not sure what happened, you should ask a hearing to the king...'
                raise AzoufzoufException(mg)
        yield from self._emit('\n')
        
    def _highlight(self, lang, code):
        try:
            lexer = get_lexer_by_name(lang)
        except ClassNotFound:
            return '<pre>%s</pre>' % code
        else:
            return highlight(code, lexer, pygments_html_formatter)

    # start of command definition

    @is_paragraph
    def title(self, value):
        yield '<h1>'
        with self._inline():
            title = self.render(value)
        title  = ''.join(title)
        self._context['title'] = title
        yield title
        yield '</h1>'

    # helper function to define h2, h3....
    def _section(self, tag, value):
        yield '<%s>' % tag
        with self._inline():
            yield from self.render(value)
        yield '</%s>' % tag

    factory = lambda tag: is_paragraph(lambda self, value: self._section(tag, value))

    section, subsection, subsubsection, subsubsubsection, subsubsubsubsection = map(
        factory,
        ('h2', 'h3', 'h4', 'h5', 'h6')
    )

    def list(self, items):
        self._space_count = 0
        yield '<ol>'
        with self._inline():
            yield from self.render(items)
        yield '</ol>'

    def item(self, value):
        yield '<li>'
        with self._inline():
            yield from self.render(value)
        yield '</li>'

    def href(self, url, text, klass=None):
        with self._inline():           
            if klass:
                url, text, klass = map(compose(self.render, ''.join), (url, text, klass))
            else:
                url, text = map(compose(self.render, ''.join), (url, text))

        # maybe url is a reference
        try:
            url = self._context[url]
        except KeyError:
            pass

        if klass:
            yield '<a href="%s" class="%s">%s</a>' % (url, klass, text)
        else:
            yield '<a href="%s">%s</a>' % (url, text)

    def image(self, url, text):
        with self._inline():
            url, text = map(compose(self.render, ''.join), (url, text))
        yield '<img src="%s" title="%s" />' % (url, text)

    def code(self, text, klass=None):
        with self._inline():
            if klass:
                text, klass = map(compose(self.render, ''.join), (text, klass))
                text = escape(text)
                yield '<code class="%s">%s</code>' % (klass, text)
            else:
                text = ''.join(self.render(text))
                yield '<code>%s</code>' % text
    
    def include(self, value):
        with self._inline():
            filepath = ''.join(self.render(value))

        with open(os.path.join(self._basepath, filepath)) as f:
            code = f.read()
        _, lang = os.path.splitext(filepath)
        lang = lang[1:]
        code = self._highlight(lang, code)
        code = '<div class=include>%s</div>' % code
        yield code

    @is_paragraph        
    def require(self, filepath):
        with self._inline():
            filepath = ''.join(self.render(filepath))
        fullpath = os.path.join(self._basepath, filepath)
        basepath = os.path.dirname(fullpath)
        with open(fullpath) as f:
            output = render(f.read(), dict(self._context), basepath)
        body = output['body']
        return body

    def context(self, value):
        with self._inline():
            value = ''.join(self.render(value))
        yield self._context[value]

    @is_paragraph
    def highlight(self, lang, code):
        with self._inline():
            lang = ''.join(self.render(lang))
        with self._verbatim():
            code = ''.join(self.render(code))
        print('lang', lang.split('\n'))
        code = self._highlight(lang, code)
        yield code


_render = HTMLRender()


def render(source, context=None, basepath=None):
    """render a azf string to html using the default html renderer"""
    if not context:
        context = dict()
    tokens = parse(source)
    output = _render(tokens, context, basepath)
    return output

        
class JinjaRender:

    def __init__(self, *paths, **filters):
        paths = map(os.path.abspath, paths)
        self.environment = Environment(
            loader=FileSystemLoader(paths),
        )
        self.environment.filters.update(filters)

    def __call__(self, template, context):
        template = self.environment.get_template(template)
        out = template.render(**context)
        return out


def jinja(template, context, *paths, **filters):
    render = JinjaRender(*paths, **filters)
    output = render(template, context)
    return output


# if __name__ == '__main__':
#     # main.py publish note <path>
#     # main.py publish page <path>
#     # main.py dung <path> [<output>] [--pretty-print=<indent>] [--ugly]
#     # main.py render html <path>
#     # main.py render jinja2 <template> <context> <output>
#     # main.py build

#     doc = """make.py.

# Usage:
#   make.py build --dev
#   make.py build [<path>]
#   make.py -h | --help
#   make.py --version

# Options:
#   -h --help               Show this screen.
#   --version               Show version.
# """
#     arguments = docopt(doc, version='15.01.29')
#     print(arguments)
#     main(arguments)


# # TEST ################################################################################################
