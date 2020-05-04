from libcst import SimpleWhitespace, List, Tuple, Set, Dict, Parameters, Call, ClassDef, MaybeSentinel
from libcst.metadata import ParentNodeProvider

from .base import BaseChecker


class CommaSpacing(BaseChecker):
    NAME = 'comma_spacing'
    DESCRIPTION = 'Checks the compliance with spacing rules around commas.'
    OPTIONS = {}
    MESSAGES = {
        'missing-trailing-comma-whitespace': {
            'template': "Missing whitespace after {!r}.",
            'description': """
            """,
        },
        'extra-leading-comma-whitespace': {
            'template': "Extraneous whitespace before {!r}.",
            'description': """
            """,
        },
        'extra-trailing-comma-whitespace': {
            'template': "Extraneous whitespace after {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def visit_Comma(self, node):
        whitespace_before_node = node.whitespace_before
        leading = whitespace_before_node.value
        if leading != '':
            self.add_error('extra-leading-comma-whitespace', node=node, args=(',',))

        whitespace_after_node = node.whitespace_after
        if isinstance(whitespace_after_node, SimpleWhitespace):
            trailing = whitespace_after_node.value
            grandparent_node = self.get_metadata(ParentNodeProvider, self.get_metadata(ParentNodeProvider, node))

            # Tuples with one item require a trailing comma with no whitespace after
            # All other cases require a space after a comma
            if isinstance(grandparent_node, Tuple) and len(grandparent_node.elements) == 1:
                if trailing != '':
                    self.add_error('extra-trailing-comma-whitespace', node=node, args=(',',))
                else:
                    return

            # This block checks for trailing commas, that are ignored because
            # handled by another checker TODO: link to checker
            if isinstance(grandparent_node, (Tuple, List, Set, Dict)):
                if grandparent_node.elements[-1].comma is node:
                    return
            elif isinstance(grandparent_node, Parameters):
                # Build the parameters list, hopefully in the right order
                parameters = grandparent_node.posonly_params + grandparent_node.params
                if grandparent_node.star_arg is not MaybeSentinel.DEFAULT:
                    parameters += (grandparent_node.star_arg,)
                parameters += grandparent_node.kwonly_params
                if grandparent_node.star_kwarg is not None:
                    parameters += (grandparent_node.star_kwarg,)

                if parameters[-1].comma is node:
                    return
            elif isinstance(grandparent_node, ClassDef):
                if grandparent_node.bases[-1].comma is node:
                    return
            elif isinstance(grandparent_node, Call):
                if grandparent_node.args[-1].comma is node:
                    return

            if trailing.startswith('  '):
                self.add_error('extra-trailing-comma-whitespace', node=node, args=(',',))
            elif trailing != ' ':
                self.add_error('missing-trailing-comma-whitespace', node=node, args=(',',))
        else:
            first_line_node = whitespace_after_node.first_line
            if first_line_node.comment is not None:
                return

            if first_line_node.whitespace.value != '':
                self.add_error('extra-trailing-comma-whitespace', node=node, args=(',',))
