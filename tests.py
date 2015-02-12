from unittest import TestCase

from azf import parse
from azf import render

from json import dumps


class TestParser(TestCase):

    maxDiff = None
    
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
    
    maxDiff = None

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
