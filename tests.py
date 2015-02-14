import os
from tempfile import mkdtemp
from unittest import TestCase
from shutil import rmtree

from azf import parse
from azf import HTML
from azf import Jinja
from azf import AzoufzoufException

from json import dumps


# lazy fixes to support new render signature
def render(source, context=None, basepath=None):
    if not context:
        context = dict()
    return HTML.render(source, basepath, **context)

def jinja(template, context, *paths, **filters):
    return Jinja.render(template, *paths, filters=filters, **context)



class TestParser(TestCase):

    def test_single_line(self):
        text = """héllo there what happened to you lately?"""
        output = list(parse(text))
        expected = [
            {'kind': 'text', 'value': 'héllo there what happened to you lately?'},
        ]
        self.assertEqual(output, expected)

    def test_two_lines(self):
        text = """héllo there what happened to you lately? I know
you have been up to something, don't you?"""
        output = list(parse(text))
        expected = [
            {'kind': 'text', 'value': 'héllo there what happened to you lately? I know'},
            {'kind': 'eol'},
            {'kind': 'text', 'value': "you have been up to something, don't you?"}
        ]
        self.assertEqual(output, expected)

    def test_two_paragraphs_with_eol_end(self):
        text = """héllo there what happened to you lately? I know
you have been up to something, don't you?

You don't want to tell me? So do I! You won't hear
a thing from me.
"""
        output = list(parse(text))
        expected = [
            {'kind': 'text', 'value': 'héllo there what happened to you lately? I know'},
            {'kind': 'eol'},
            {'kind': 'text', 'value': "you have been up to something, don't you?"},
            {'kind': 'eol'},
            {'kind': 'eol'},
            {'kind': 'text', 'value': "You don't want to tell me? So do I! You won't hear"},
            {'kind': 'eol'},
            {'kind': 'text', 'value': "a thing from me."},
            {'kind': 'eol'},
        ]
        self.assertEqual(output, expected)


    def test_text_with_dash_over_several_lines(self):
        text = """- héllo there what happened to you lately?
- So much :)

- Good to see you"""
        output = list(parse(text))
        expected = [
            {'kind': 'text', 'value': '- héllo there what happened to you lately?'},
            {'kind': 'eol'},
            {'kind': 'text', 'value': '- So much :)'},
            {'kind': 'eol'},
            {'kind': 'eol'},
            {'kind': 'text', 'value': '- Good to see you'}
        ]
        self.assertEqual(output, expected)


    def test_single_simple_command(self):
        text = """ⵣBBB"""
        output = list(parse(text))
        expected = [
            {'value': 'BBB', 'arguments': (), 'kind': 'command'},
        ]
        self.assertEqual(expected, output)

    def test_single_simple_command_with_text_before(self):
        text = """AAA ⵣBBB"""
        output = list(parse(text))
        expected = [
            {'value': 'AAA ', 'kind': 'text'},
            {'value': 'BBB', 'arguments': (), 'kind': 'command'},
        ]
        self.assertEqual(expected, output)

    def test_single_simple_command_with_text_after(self):
        text = """ⵣBBB CCC"""
        output = list(parse(text))
        expected = [
            {'value': 'BBB', 'arguments': (), 'kind': 'command'},
            {'value': ' CCC', 'kind': 'text'}
        ]
        self.assertEqual(expected, output)

    def test_several_simple_commands(self):
        text = """ⵣAAA ⵣBBB ⵣCCC"""
        output = list(parse(text))
        expected = [
            {'value': 'AAA', 'arguments': (), 'kind': 'command'},
            {'value': ' ', 'kind': 'text'},
            {'value': 'BBB', 'arguments': (), 'kind': 'command'},
            {'value': ' ', 'kind': 'text'},
            {'value': 'CCC', 'arguments': (), 'kind': 'command'},
        ]
        self.assertEqual(expected, output)

    def test_several_simple_commands_without_space(self):
        text = """ⵣAAAⵣBBBⵣCCC"""
        output = list(parse(text))
        expected = [
            {'value': 'AAA', 'arguments': (), 'kind': 'command'},
            {'value': 'BBB', 'arguments': (), 'kind': 'command'},
            {'value': 'CCC', 'arguments': (), 'kind': 'command'},
        ]
        self.assertEqual(expected, output)

    def test_several_commands_with_arguments_and_without_space(self):
        text = """ⵣAAA{111}{222}ⵣBBB{333}{444}"""
        output = list(parse(text))
        expected = [
            {
                'value': 'AAA',
                'arguments': [
                    [{'kind': 'text', 'value': '111'}],
                    [{'kind': 'text', 'value': '222'}]
                ],
                'kind': 'command'},
            {
                'value': 'BBB',
                'arguments': [
                    [{'kind': 'text', 'value': '333'}],
                    [{'kind': 'text', 'value': '444'}]
                ],
                'kind': 'command'
            },
        ]
        self.assertEqual(expected, output)

    def test_command_without_args(self):
        text = """AAA ⵣBBB CCC"""
        output = list(parse(text))
        expected = [
            {'value': 'AAA ', 'kind': 'text'},
            {'value': 'BBB', 'arguments': (), 'kind': 'command'},
            {'value': ' CCC', 'kind': 'text'}
        ]
        self.assertEqual(expected, output)

    def test_command_with_one_single_word_arg(self):
        text = """AAA ⵣBBB{111} CCC"""
        output = list(parse(text))
        expected = [
            {'value': 'AAA ', 'kind': 'text'},
            {'arguments': [
                [
                    {'value': '111', 'kind': 'text'}
                ]
            ],
             'value': 'BBB', 'kind': 'command'},
            {'value': ' CCC', 'kind': 'text'}
        ]
        self.assertEqual(expected, output)

    def test_command_with_two_args(self):
        text = """AAA ⵣBBB{111}{222} CCC"""
        output = list(parse(text))
        expected = [
            {'value': 'AAA ', 'kind': 'text'},
            {'arguments': [
                [{'value': '111', 'kind': 'text'}],
                [{'value': '222', 'kind': 'text'}],
            ],
             'value': 'BBB', 'kind': 'command'},
            {'value': ' CCC', 'kind': 'text'}
        ]
        self.assertEqual(expected, output)


    def test_command_with_several_words_arg(self):
        text = """AAA ⵣBBB{111 222} CCC"""
        output = list(parse(text))
        expected = [
            {'value': 'AAA ', 'kind': 'text'},
            {'arguments': [
                [
                    {'value': '111 222', 'kind': 'text'}
                ]
            ],
             'value': 'BBB', 'kind': 'command'},
            {'value': ' CCC', 'kind': 'text'}
        ]
        self.assertEqual(expected, output)


    def test_command_with_one_arg_and_nested_command(self):
        text = """AAA ⵣBBB{111 ⵣ222 333} CCC"""
        output = list(parse(text))
        expected = [
            {'kind': 'text', 'value': 'AAA '},
            {
                'kind': 'command',
                'arguments': [[{'kind': 'text', 'value': '111 '},
                               {'kind': 'command', 'arguments': (), 'value': '222'},
                               {'kind': 'text', 'value': ' 333'}]],
                'value': 'BBB',
            },
            {'kind': 'text', 'value': ' CCC'},
        ]
        self.assertEqual(expected, output)

    def test_command_with_one_arg_with_nested_command_with_arg(self):
        text = """ⵣBBB{111 ⵣ222{zzz} 333}"""
        output = list(parse(text))
        expected = [{
                'kind': 'command',
                'arguments': [[
                    {'kind': 'text', 'value': '111 '},
                    {'kind': 'command', 'arguments': [[{'kind': 'text', 'value': 'zzz'}]], 'value': '222'},
                    {'kind': 'text', 'value': ' 333'}
                ]],
             'value': 'BBB'
        }]

        self.assertEqual(expected, output)

    def test_text_and_command_with_one_arg_with_nested_command_with_arg(self):
        text = """AAA ⵣBBB{111 ⵣ222{zzz} 333} CCC"""
        output = list(parse(text))
        expected = [
            {'value': 'AAA ', 'kind': 'text'},
            {
                'arguments': [[
                    {'value': '111 ', 'kind': 'text'},
                    {'arguments': [[{'value': 'zzz', 'kind': 'text'}]], 'value': '222', 'kind': 'command'},
                    {'value': ' 333', 'kind': 'text'}
                ]],
                'value': 'BBB',
                'kind': 'command'
            },
            {'value': ' CCC', 'kind': 'text'}
        ]
        self.assertEqual(expected, output)

    def test_command_with_several_args_with_a_nested_command_with_args(self):
        text = """AAA ⵣBBB{111 ⵣ222{zzz}{yyy} 333} CCC"""
        output = list(parse(text))
        expected = [
            {'value': 'AAA ', 'kind': 'text'},
            {
                'arguments': [[{'value': '111 ', 'kind': 'text'}, {'arguments': [[{'value': 'zzz', 'kind': 'text'}], [{'value': 'yyy', 'kind': 'text'}]], 'value': '222', 'kind': 'command'}, {'value': ' 333', 'kind': 'text'}]],
                'value': 'BBB',
                'kind': 'command'
            },
            {'value': ' CCC', 'kind': 'text'}
        ]
        self.assertEqual(expected, output)


    def test_text_with_curly_braces(self):
        text = """function(a, b, c) { return a+b+c; }"""
        output = list(parse(text))
        expected = [{'kind': 'text', 'value': 'function(a, b, c) { return a+b+c; }'}]
        self.assertEqual(expected, output)

    def test_text_with_curly_braces_over_several_lines(self):
        text = """function(a, b, c) {
return a+b+c;
}"""
        output = list(parse(text))
        expected = [
            {'kind': 'text', 'value': 'function(a, b, c) {'},
            {'kind': 'eol'},
            {'kind': 'text', 'value': 'return a+b+c;'},
            {'kind': 'eol'},
            {'kind': 'text', 'value': '}'}
        ]
        self.assertEqual(expected, output)

    def test_command_over_several_lines_with_curly_braces_in_arguments(self):
        text = """ⵣcode{function(a, b, c) {
return a+b+c;
}}"""
        output = list(parse(text))
        expected = [
            {'kind': 'command',
             'arguments': [[
                 {'kind': 'text', 'value': 'function(a, b, c) {'},
                 {'kind': 'eol'}, {'kind': 'text', 'value': 'return a+b+c;'},
                 {'kind': 'eol'},
                 {'kind': 'text', 'value': '}'}
             ]],
             'value': 'code'}
        ]
        self.assertEqual(expected, output)

    def test_command_with_curly_braces_in_arguments(self):
        text = """ⵣcode{function(a, b, c) {return a+b+c;}}"""
        output = list(parse(text))
        expected = [{
            'arguments': [[{'value': 'function(a, b, c) {return a+b+c;}', 'kind': 'text'}]],
            'kind': 'command',
            'value': 'code',
        }]
        self.assertEqual(expected, output)



class TestHTMLRender(TestCase):

    def test_unknown_command(self):
        text = """héllo there what happened to ⵣyou lately?"""
        with self.assertRaises(AzoufzoufException):
            render(text)

    def test_single_command(self):
        self.assertEqual("ⵣazecv", "<p>azecv</p>")

    def test_single_command_is_paragraph(self):
        self.assertEqual("ⵣazecv", "azecv")

    def test_single_line(self):
        text = """héllo there what happened to you lately?"""
        output = render(text)['body']
        expected = '<p>héllo there what happened to you lately?</p>'
        self.assertEqual(output, expected)

    def test_two_lines(self):
        text = """héllo there what happened to you lately? I know
you have been up to something, don't you?"""
        output = render(text)['body']
        expected = "<p>héllo there what happened to you lately? I know you have been up to something, don't you?</p>"
        self.assertEqual(output, expected)

    def test_two_paragraphs_with_eol_end(self):
        text = """héllo there what happened to you lately? I know
you have been up to something, don't you?

You don't want to tell me? So do I! You won't hear
a thing from me.
"""
        output = render(text)['body']
        expected = "<p>héllo there what happened to you lately? I know you have been up to something, don't you?</p><p>You don't want to tell me? So do I! You won't hear a thing from me.</p>"
        self.assertEqual(output, expected)

    def test_one_long_paragraph_over_several_lines(self):
        text = """héllo there what happened to you lately? I know
you have been up to something, don't you?
You don't want to tell me? So do I! You won't hear
a thing from me.
"""
        output = render(text)['body']
        expected = "<p>héllo there what happened to you lately? I know you have been up to something, don't you? You don't want to tell me? So do I! You won't hear a thing from me.</p>"
        self.assertEqual(output, expected)

        
    def test_text_with_dash_over_several_lines(self):
        text = """- héllo there what happened to you lately?

- So much :)

- Good to see you"""
        output = render(text)['body']
        expected = "<p>- héllo there what happened to you lately?</p><p>- So much :)</p><p>- Good to see you</p>"
        self.assertEqual(output, expected)

    def test_command_title(self):
        text = """ⵣtitle{Become rich, successul & respected}"""
        output = render(text)
        self.assertEqual(output['body'], '<h1>Become rich, successul & respected</h1>')
        self.assertEqual(output['title'], 'Become rich, successul & respected')

    def test_section_command(self):
        text = 'ⵣsection{Introduction}'
        output = render(text)['body']
        self.assertEqual(output, '<h2>Introduction</h2>')

    def test_list(self):
        text = """
ⵣlist{
  ⵣitem{eggs}
  ⵣitem{apple}
  ⵣitem{lettuce}
  ⵣitem{what else ?}
}
"""
        output = render(text)['body']
        self.assertEqual(output, '<ol>   <li>eggs</li>   <li>apple</li>   <li>lettuce</li>   <li>what else ?</li> </ol>')

    def test_nested_list(self):
        text = """
ⵣlist{
  ⵣitem{vegatables
    ⵣlist{
      ⵣitem{tomato}
      ⵣitem{lettuce}
      ⵣitem{beans}
  }}
  ⵣitem{meats}
}
"""
        output = render(text)['body']
        self.assertEqual(output, '<ol>   <li>vegatables      <ol>       <li>tomato</li>       <li>lettuce</li>       <li>beans</li>   </ol></li>   <li>meats</li> </ol>')

    def test_href(self):
        text = 'ⵣhref{http://URL}{TEXT}'
        output = render(text)['body']
        self.assertEqual(output, '<a href="http://URL">TEXT</a>')

    def test_href_with_klass(self):
        text = 'ⵣhref{http://URL}{TEXT}{CSS CLASS}'
        output = render(text)['body']
        self.assertEqual(output, '<a href="http://URL" class="CSS CLASS">TEXT</a>')

    def test_image(self):
        text = 'ⵣimage{http://URL}{TEXT}'
        output = render(text)['body']
        self.assertEqual(output, '<img src="http://URL" title="TEXT" />')

    def test_code(self):
        text = 'ⵣcode{reduce}'
        output = render(text)['body']
        self.assertEqual(output, '<code>reduce</code>')

    def test_code_with_klass(self):
        text = 'ⵣcode{reduce}{python}'
        output = render(text)['body']
        self.assertEqual(output, '<code class="python">reduce</code>')

    def test_nested_code_in_section(self):
        text = 'ⵣsection{how ⵣcode{reduce} works}'
        output = render(text)['body']
        self.assertEqual(output, '<h2>how <code>reduce</code> works</h2>')

    def test_nested_code_in_section_start(self):
        text = 'ⵣsection{ⵣcode{reduce} is awesome}'
        output = render(text)['body']
        self.assertEqual(output, '<h2><code>reduce</code> is awesome</h2>')

    def test_nested_code_in_section_end(self):
        text = 'ⵣsection{The awesome ⵣcode{reduce}}'
        output = render(text)['body']
        self.assertEqual(output, '<h2>The awesome <code>reduce</code></h2>')

    def test_include(self):
        path = mkdtemp()
        with open(os.path.join(path, 'include.js'), 'w') as f:
            f.write('function troll() { return undefined;}')
        expected = """<div class=include><div class="highlight"><pre><span class="kd">function</span> <span class="nx">troll</span><span class="p">()</span> <span class="p">{</span> <span class="k">return</span> <span class="kc">undefined</span><span class="p">;}</span>\n</pre></div>\n</div>"""
        output = render("ⵣinclude{include.js}", basepath=path)['body']
        self.assertEqual(output, expected)
        rmtree(path)

    def test_include_no_lexer(self):
        path = mkdtemp()
        with open(os.path.join(path, 'include.azf'), 'w') as f:
            f.write("""Héllo!

I'd like to be included. Plz!""")
        expected = "<div class=include><pre>Héllo!\n\nI'd like to be included. Plz!</pre></div>"
        output = render("ⵣinclude{include.azf}", basepath=path)['body']
        self.assertEqual(output, expected)
        rmtree(path)

    def test_require(self):
        path = mkdtemp()
        with open(os.path.join(path, 'part.azf'), 'w') as f:
            f.write("""ⵣsection{Héllo}

I'd like to join the party. Plz!""")
        expected = "<p>blabla bla</p><h2>Héllo</h2><p>I'd like to join the party. Plz!</p><p>blabla</p>"
        output = render("""blabla bla

ⵣrequire{part.azf}

blabla""", basepath=path)['body']
        self.assertEqual(output, expected)
        rmtree(path)

    def test_context(self):
        expected = "<p>Héllo Azoufzouf, you are tested!</p>"
        output = render(
            """Héllo ⵣcontext{name}, you are ⵣcontext{status}!""",
            dict(name="Azoufzouf", status="tested"),
        )['body']
        self.assertEqual(output, expected)

    def test_highlight(self):
        code = """function troll() {
    return undefined;
}"""
        expected = """<div class="highlight"><pre><span class="kd">function</span> <span class="nx">troll</span><span class="p">()</span> <span class="p">{</span>
    <span class="k">return</span> <span class="kc">undefined</span><span class="p">;</span>
<span class="p">}</span>
</pre></div>
"""
        output = render("ⵣhighlight{javascript}{%s}" % code)['body']
        self.assertEqual(output, expected)

    def test_custom_formatter(self):

        class CustomFormatter(HTML):

            HTML.is_paragraph
            def mycommand(self):
                yield "MYCOMMAND IS WORKING!"

        expected = "MYCOMMAND IS WORKING!"
        output = CustomFormatter.render("ⵣmycommand")['body']
        self.assertEqual(output, expected)

    def test_custom_formatter_with_require(self):

        class CustomFormatter(HTML):

            def mycommand(self):
                yield "MYCOMMAND IS WORKING!"

        expected = "MYCOMMAND IS WORKING!"
        path = mkdtemp()
        with open(os.path.join(path, 'extra.azf'), 'w') as f:
            f.write("""

ⵣmycommand

""")
        output = CustomFormatter.render("ⵣrequire{extra.azf}", path)['body']
        self.assertEqual(output, expected)
        rmtree(path)


class TestJinja(TestCase):

    def test_render_jinja(self):
        def capitalize(s):
            return s.upper()

        path = mkdtemp()
        template = 'test.jinja'
        with open(os.path.join(path, template), 'w') as f:
            f.write("Héllo {{ name }}, you are {{ status|capitalize }}! {% include 'sig.jinja' %}")
        with open(os.path.join(path, 'sig.jinja'), 'w') as f:
            f.write("Bye!")
        output = jinja(template, dict(name="Azoufazouf", status="tested"), path, capitalize=capitalize)
        self.assertEqual(output, 'Héllo Azoufazouf, you are TESTED! Bye!')
        rmtree(path)
