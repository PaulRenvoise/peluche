from libcst import ClassDef, ExceptHandler, SimpleWhitespace
from libcst.metadata import ParentNodeProvider

from .base import BaseChecker


class BracketSpacing(BaseChecker):
    NAME = 'bracket_spacing'
    DESCRIPTION = 'Checks for correct spacing between brackets.'
    OPTIONS = {}
    MESSAGES = {
        'missing-leading-bracket-whitespace': {
            'template': "Missing whitespace before {!r}.",
            'description': """
            """,
        },
        'extra-leading-bracket-whitespace': {
            'template': "Extraneous whitespace before {!r}.",
            'description': """
            """,
        },
        'extra-trailing-bracket-whitespace': {
            'template': "Extraneous whitespace after {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def visit_LeftSquareBracket(self, node):
        whitespace_after_node = node.whitespace_after
        if isinstance(whitespace_after_node, SimpleWhitespace):
            if whitespace_after_node.value != '':
                self.add_error('extra-trailing-bracket-whitespace', node=node, args=('[',))
        else:
            trailing = whitespace_after_node.first_line.whitespace.value
            if trailing != '':
                self.add_error('extra-trailing-bracket-whitespace', node=node, args=('[',))

    def visit_RightSquareBracket(self, node):
        whitespace_before_node = node.whitespace_before
        if isinstance(whitespace_before_node, SimpleWhitespace):
            if whitespace_before_node.value != '':
                self.add_error('extra-leading-bracket-whitespace', node=node, args=(']',))
        else:
            leading = whitespace_before_node.first_line.whitespace.value
            if leading != '':
                self.add_error('extra-leading-bracket-whitespace', node=node, args=(']',))
