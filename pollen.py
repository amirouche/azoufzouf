def parse(file):
    with open(file) as f:
        string = f.read()
    return from_string(string)


def from_string(string):
    output = list()
    context = dict()
    # init loop
    next = string[0]
    string = string[1:]
    while string:
        if next == '◊':
            next = string[0]
            string = string[1:]
            command_name = ''
            while True:
                if next.isalpha():
                    command_name += next
                    next = string[0]
                    string = string[1:]
                else:  # command fully parsed
                    break
            # parse arguments if any
            if next == '[':
                # parse argument, only one argument is supported
                # it can be a string or a variable
                next = string[0]
                string = string[1:]
                argument_kind = ''
                if next == '"':
                    # it's a string
                    argument_kind = 'string'
                    next = string[0]
                    string = string[1:]
                    argument = ''
                    while True:
                        if next == '"':
                            next = string[0]
                            string = string[1:]
                            break
                        else:
                            argument += next
                            next = string[0]
                            string = string[1:]
                else:
                    # fallback to variable
                    argument_kind = 'variable'
                    # no need to skip
                    argument = ''
                    while True:
                        if next.isalpha():
                            argument += next
                            next = string[0]
                            string = string[1:]
                        else:
                            break
                    # retrieve value
                    value = context[argument]
                    # change node kind
                    argument_kind = 'string'
                    argument = value
                    next = string[0]
                    string = string[1:]
                    import ipdb; ipdb.set_trace()
            else:
                argument_kind = None
                argument = None
            # parse text if any
            if next == '{':
                # parse string, it is not recursive
                next = string[0]
                string = string[1:]
                text = ''
                while True:
                    if next == '}' and len(string) > 0 and string[0] != '}':
                        # skip closing curly bracket
                        next = string[0]
                        string = string[1:]
                        break
                    else:
                        text += next
                        next = string[0]
                        string = string[1:]
            else:
                text = None
            if command_name == 'set':
                # only update context
                context[argument] = text
            else:
                # add command to output with full specification
                command = dict(
                    kind='command',
                    name=command_name,
                )
                if argument:
                    command['argument'] = argument
                if text:
                    command['text'] = text
                output.append(command)
        else:
            paragraph = ''
            while string and next != '◊':
                paragraph += next
                next = string[0]
                string = string[1:]
            paragraph = dict(kind='text', value=paragraph)
            output.append(paragraph)
    return output
