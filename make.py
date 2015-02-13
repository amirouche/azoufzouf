#!/usr/bin/env python3
import os

from azf import HTML
from azf import Jinja
     

if __name__ == '__main__':
    path = os.path.abspath(__file__)
    path = os.path.dirname(path)
    with open('index.azf') as f:
        context = HTML.render(f.read(), path)
    output = Jinja.render('index.jinja', path, **context)
    with open('index.html', 'w') as f:
        f.write(output)
