from libcst import EmptyLine
from libcst.metadata import PositionProvider, ParentNodeProvider
from libcst.matchers import findall, ClassDef, FunctionDef, Comment

from .base import BaseChecker


class ModuleLength(BaseChecker):
    NAME = 'module_length'
    DESCRIPTION = 'Checks the maximum length of modules.'
    OPTIONS = {
        'max': {
            'default': 225,  # TODO: Use the default max size of classes and functions to give space for stuff like imports
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
        'module-too-long': {
            'template': "Module is too long ({!r}/{!r}).",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    # TODO: align on docstring style and take it in account here
    # when counting the docstring delimiters' size
    def visit_Module(self, node):
        position = self.get_metadata(PositionProvider, node)
        length = position.length

        if True:
            docstring = node.get_docstring()
            if docstring is not None:
                length -= len(docstring.splitlines()) + 2  # Docstring delimiters

            methods = findall(node, FunctionDef())
            for method in methods:
                docstring = method.get_docstring()
                if docstring is not None:
                    length -= len(docstring.splitlines()) + 2  # Docstring delimiters

            clses = findall(node, ClassDef())
            for cls in clses:
                docstring = cls.get_docstring()
                if docstring is not None:
                    length -= len(docstring.splitlines()) + 2  # Docstring delimiters

        if True:
            comments = findall(node, Comment())
            for comment in comments:
                parent_node = self.get_metadata(ParentNodeProvider, comment)
                if isinstance(parent_node, EmptyLine):  # The comment is not inline
                    length -= 1  # One comment = one line

        if length > 225:
            self.add_error('module-too-long', node=node, args=(length, 225))
