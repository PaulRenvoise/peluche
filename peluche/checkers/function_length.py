from libcst import EmptyLine
from libcst.metadata import PositionProvider, ParentNodeProvider
from libcst.matchers import findall, FunctionDef, Comment

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
        'ignore-comments': {
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

    # TODO: align on docstring style and take it in account here
    # when counting the docstring delimiters' size
    def visit_FunctionDef(self, node):
        position = self.get_metadata(PositionProvider, node)
        length = position.length - 1  # Minus one for the function's signature

        if True:
            docstring = node.get_docstring()
            if docstring is not None:
                length -= len(docstring.splitlines()) + 2 # Docstring delimiters

            # We might have nested functions that are documented...
            nested_functions = findall(node, FunctionDef())
            for nested_function in nested_functions:
                docstring = nested_function.get_docstring()
                if docstring is not None:
                    length -= len(docstring.splitlines()) + 2 # Docstring delimiters

        if True:
            comments = findall(node, Comment())
            for comment in comments:
                parent_node = self.get_metadata(ParentNodeProvider, comment)
                if isinstance(parent_node, EmptyLine):  # The comment is not inline
                    length -= 1  # One comment = one line

        if length > 25:
            self.add_error('function-too-long', node=node, args=(length, 25))
