from .base import BaseChecker


class FunctionLength(BaseChecker):
    NAME = 'function_length'
    DESCRIPTION = 'Checks the maximum length of functions.'
    OPTIONS = {
        'max': {
            'default': 25,
            'type': 'int',
            'metavar': 'LENGTH',
            'help': """
                The maximum length allowed.
            """,
        },
        'ignore-docstrings': {
            'default': True,
            'type': 'bool',
            'metavar': 'TRUE or FALSE',
            'help': """
                Whether or not to ignore docstrings.
            """
        },
        'ignore-comments': {  # TODO
            'default': True,
            'type': 'bool',
            'metavar': 'TRUE or FALSE',
            'help': """
                Whether or not to ignore comments.
            """
        },
    }
    MESSAGES = {
        'function-too-long': {
            'template': "Function is too long ({!r}/{!r}).",
            'description': """
                Implementing long functions reduces readbility, understandability,
                and increases difficulty to correctly test.
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_def(self, node):
        length = node.absolute_length - 1  # Minus one for the function's signature

        if True:
            docstring = node.value.find('string')

            if docstring is not None and docstring.parent == node:
                length -= docstring.absolute_length

        if length > 25:
            self.add_error('function-too-long', node=node, args=(length, 25))
