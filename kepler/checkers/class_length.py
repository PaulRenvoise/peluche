from .base import BaseChecker


class ClassLength(BaseChecker):
    NAME = 'class_length'
    DESCRIPTION = 'Checks the maximum length of classes.'
    OPTIONS = {
        'max': {
            'default': 200,
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
        'class-too-long': {
            'template': "Class is too long ({!r}/{!r}).",
            'description': """
                Implementing long classes reduces readability, understandability,
                and cohesion.
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_class(self, node):
        length = node.absolute_length - 1

        if True:
            docstrings = node.value.find_all('string')

            for docstring in docstrings:
                if docstring.parent.type in ('def', 'class'):
                    length -= docstring.absolute_length

        if length > 200:
            self.add_error('class-too-long', node=node, args=(length, 200))
