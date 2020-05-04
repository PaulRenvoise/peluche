from libcst import ClassDef, ExceptHandler, SimpleWhitespace
from libcst.metadata import ParentNodeProvider

from .base import BaseChecker


class ParenthesesSpacing(BaseChecker):
    NAME = 'parentheses_spacing'
    DESCRIPTION = 'Checks for correct spacing between parentheses.'
    OPTIONS = {}
    MESSAGES = {
        'missing-leading-parenthesis-whitespace': {
            'template': "Missing whitespace before {!r}.",
            'description': """
            """,
        },
        'extra-leading-parenthesis-whitespace': {
            'template': "Extraneous whitespace before {!r}.",
            'description': """
            """,
        },
        'extra-trailing-parenthesis-whitespace': {
            'template': "Extraneous whitespace after {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def visit_LeftParen(self, node):
        parent_node = self.get_metadata(ParentNodeProvider, node)
        if isinstance(parent_node, ClassDef):
            if parent_node.whitespace_after_name.value != '':
                self.add_error('extra-leading-parenthesis-whitespace', node=node, args=('(',))
        else:
            grandparent_node = self.get_metadata(ParentNodeProvider, parent_node)
            if isinstance(grandparent_node, ExceptHandler):
                whitespace = grandparent_node.whitespace_after_except.value
                if whitespace.startswith('  '):
                    self.add_error('extra-leading-parenthesis-whitespace', node=node, args=('(',))
                elif whitespace != ' ':
                    self.add_error('missing-leading-parenthesis-whitespace', node=node, args=('(',))

        self._check_whitespace(node, node.whitespace_after, 'extra-trailing-parenthesis-whitespace', '(')

    def visit_RightParen(self, node):
        self._check_whitespace(node, node.whitespace_before, 'extra-leading-parenthesis-whitespace', ')')

    # TODO: find the correct paren node position
    def visit_FunctionDef(self, node):
        if node.whitespace_after_name.value != '':
            self.add_error('extra-leading-parenthesis-whitespace', node=node, args=('(',))

        self._check_whitespace(node, node.whitespace_before_params, 'extra-trailing-parenthesis-whitespace', '(')

        if node.params.params:
            whitespace_after_param_node = node.params.params[-1].whitespace_after_param
            self._check_whitespace(node, whitespace_after_param_node, 'extra-leading-parenthesis-whitespace', ')')

        if node.whitespace_before_colon.value != '':
            self.add_error('extra-trailing-parenthesis-whitespace', node=node, args=(')',))

    # TODO: find the correct paren node position
    def visit_Call(self, node):
        if node.whitespace_after_func.value != '':
            self.add_error('extra-leading-parenthesis-whitespace', node=node, args=('(',))

        self._check_whitespace(node, node.whitespace_before_args, 'extra-trailing-parenthesis-whitespace', ')')

        if node.args:
            self._check_whitespace(node, node.args[-1].whitespace_after_arg, 'extra-leading-parenthesis-whitespace', ')')

    def _check_whitespace(self, node, whitespace_node, message, symbol):
        if isinstance(whitespace_node, SimpleWhitespace):
            if whitespace_node.value != '':
                self.add_error(message, node=node, args=(symbol,))
        else:
            first_line_node = whitespace_node.first_line
            if first_line_node.comment is not None:
                return

            if first_line_node.whitespace.value != '':
                self.add_error(message, node=node, args=(symbol,))
