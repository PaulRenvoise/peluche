from libcst import EmptyLine
from libcst.metadata import PositionProvider, ParentNodeProvider
from libcst.matchers import findall, FunctionDef, Comment

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

    # TODO: align on docstring style and take it in account here
    # when counting the docstring delimiters' size
    def visit_ClassDef(self, node):
        position = self.get_metadata(PositionProvider, node)
        length = position.length - 1 # Minus one for the class' header

        if True:
            docstring = node.get_docstring()
            if docstring is not None:
                length -= len(docstring.splitlines()) + 2  # Docstring delimiters

            methods = findall(node, FunctionDef())
            for method in methods:
                docstring = method.get_docstring()
                if docstring is not None:
                    length -= len(docstring.splitlines()) + 2  # Docstring delimiters

        if True:
            comments = findall(node, Comment())
            for comment in comments:
                parent_node = self.get_metadata(ParentNodeProvider, comment)
                if isinstance(parent_node, EmptyLine):  # The comment is not inline
                    length -= 1  # One comment = one line

        if length > 200:
            self.add_error('class-too-long', node=node, args=(length, 200))
