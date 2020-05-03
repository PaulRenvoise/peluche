import re
from libcst.metadata import ParentNodeProvider
from libcst import EmptyLine, TrailingWhitespace, Module

from .base import BaseChecker


class CommentSpacing(BaseChecker):
    NAME = 'comment_spacing'
    DESCRIPTION = 'Checks the compliance with spacing rules before comments.'
    OPTIONS = {}
    MESSAGES = {
        'missing-leading-comment-whitespace': {
            'template': "Missing whitespace before {!r}.",
            'description': """
            """,
        },
        'missing-trailing-comment-whitespace': {
            'template': "Missing whitespace after {!r}.",
            'description': """
            """,
        },
        'extra-leading-comment-whitespace': {
            'template': "Extraneous whitespace before {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def visit_Comment(self, node):
        parent_node = self.get_metadata(ParentNodeProvider, node)
        if isinstance(parent_node, EmptyLine):  # The comment is not inline
            if not parent_node.indent:
                self.add_error('missing-leading-comment-whitespace', node=node, args=('#',))
            else:
                whitespace = parent_node.whitespace.value
                if whitespace != '':
                    self.add_error('extra-leading-comment-whitespace', node=node, args=('#',))
        else:
            whitespace = parent_node.whitespace.value
            if whitespace.startswith('   '):
                self.add_error('extra-leading-comment-whitespace', node=node, args=('#',))
            elif whitespace != '  ':
                self.add_error('missing-leading-comment-whitespace', node=node, args=('#',))

        comment = node.value
        if comment == '#':  # probably a newline, ignore
            return
        elif comment[:2] != '# ':
            self.add_error('missing-trailing-comment-whitespace', node=node, args=('#',))
