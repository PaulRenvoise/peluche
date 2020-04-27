from .base import BaseChecker


class ModuleLength(BaseChecker):
    NAME = 'module_length'
    DESCRIPTION = 'Checks the maximum length of modules.'
    OPTIONS = {
        'max': {
            'default': 225,  # Use the default max size of classes and functions to give space for stuff like imports
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
        'module-too-long': {
            'template': "Module is too long ({!r}/{!r}).",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_module(self, node):
        length = node.absolute_length

        if True:
            docstrings = node.find_all('string')

            for docstring in docstrings:
                if docstring.parent is node.root or docstring.parent.type in ('def', 'class'):
                    length -= docstring.absolute_length

        if length > 225:
            self.add_error('module-too-long', node=node, args=(length, 225))
