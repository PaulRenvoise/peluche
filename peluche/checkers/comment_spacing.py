import re
from libcst.metadata import ParentNodeProvider
from libcst import EmptyLine, ParenthesizedWhitespace, IndentedBlock, Module

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

    INDENT_STR = '    '  # FIXME: make that configurable

    def __init__(self):
        super().__init__()

    def visit_Comment(self, node):
        parent_node = self.get_metadata(ParentNodeProvider, node)
        if isinstance(parent_node, EmptyLine):  # The comment is not inline
            # Handes comments nested in non-indented block, e.g. multiline lists
            grandparent_node = self.get_metadata(ParentNodeProvider, parent_node)
            if isinstance(grandparent_node, ParenthesizedWhitespace):
                if parent_node.whitespace.value == grandparent_node.last_line.value:
                    return

                if len(parent_node.whitespace.value) > len(grandparent_node.last_line.value):
                    self.add_error('extra-leading-comment-whitespace', node=node, args=('#',))
                else:
                    self.add_error('missing-leading-comment-whitespace', node=node, args=('#',))
            else:
                # Here we handle comments within indented blocks, e.g. class/functions/methods
                expected_indent = ''
                hierarchy_node = node
                while not isinstance(hierarchy_node, Module):
                    hierarchy_node = self.get_metadata(ParentNodeProvider, hierarchy_node)
                    if isinstance(hierarchy_node, IndentedBlock):
                        expected_indent += self.INDENT_STR

                whitespace_value = parent_node.whitespace.value
                if parent_node.indent:
                    whitespace_value += expected_indent

                if whitespace_value == expected_indent:
                    return

                if len(whitespace_value) > len(expected_indent):
                    self.add_error('extra-leading-comment-whitespace', node=node, args=('#',))
                else:
                    self.add_error('missing-leading-comment-whitespace', node=node, args=('#',))
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
