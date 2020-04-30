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

        whitespace_after_node = node.whitespace_after
        if isinstance(whitespace_after_node, SimpleWhitespace):
            if whitespace_after_node.value != '':
                self.add_error('extra-trailing-parenthesis-whitespace', node=node, args=('(',))
        else:
            trailing = whitespace_after_node.first_line.whitespace.value
            if trailing != '':
                self.add_error('extra-trailing-parenthesis-whitespace', node=node, args=('(',))

    def visit_RightParen(self, node):
        whitespace_before_node = node.whitespace_before
        if isinstance(whitespace_before_node, SimpleWhitespace):
            if whitespace_before_node.value != '':
                self.add_error('extra-leading-parenthesis-whitespace', node=node, args=(')',))
        else:
            leading = whitespace_before_node.first_line.whitespace.value
            if leading != '':
                self.add_error('extra-leading-parenthesis-whitespace', node=node, args=(')',))

    def visit_FunctionDef(self, node):
        if node.whitespace_after_name.value != '':
            # TODO: find the correct position
            self.add_error('extra-leading-parenthesis-whitespace', node=node, args=('(',))

        whitespace_before_params_node = node.whitespace_before_params
        if isinstance(whitespace_before_params_node, SimpleWhitespace):
            if whitespace_before_params_node.value != '':
                # TODO: find the correct position
                self.add_error('extra-trailing-parenthesis-whitespace', node=node, args=('(',))
        else:
            trailing = whitespace_before_params_node.first_line.whitespace.value
            if trailing != '':
                self.add_error('extra-trailing-parenthesis-whitespace', node=node, args=('(',))

        if node.params.params:
            last_param = node.params.params[-1]
            if last_param.whitespace_after_param.value != '':
                # TODO: find the correct position
                self.add_error('extra-leading-parenthesis-whitespace', node=node, args=(')',))

        if node.whitespace_before_colon.value != '':
            # TODO: find the correct position
            self.add_error('extra-trailing-parenthesis-whitespace', node=node, args=(')',))

    def visit_Call(self, node):
        if node.whitespace_after_func.value != '':
            # TODO: find the correct position
            self.add_error('extra-leading-parenthesis-whitespace', node=node, args=('(',))

        whitespace_before_args_node = node.whitespace_before_args
        if isinstance(whitespace_before_args_node, SimpleWhitespace):
            if whitespace_before_args_node.value != '':
                # TODO: find the correct position
                self.add_error('extra-trailing-parenthesis-whitespace', node=node, args=('(',))
        else:
            trailing = whitespace_before_args_node.first_line.whitespace.value
            if trailing != '':
                self.add_error('extra-trailing-parenthesis-whitespace', node=node, args=('(',))

        if node.args:
            last_arg_node = node.args[-1]
            whitespace_after_last_arg_node = last_arg_node.whitespace_after_arg
            if isinstance(whitespace_after_last_arg_node, SimpleWhitespace):
                if whitespace_after_last_arg_node.value != '':
                    # TODO: find the correct position
                    self.add_error('extra-leading-parenthesis-whitespace', node=node, args=(')',))
            else:
                trailing = whitespace_after_last_arg_node.first_line.whitespace.value
                if trailing != '':
                    self.add_error('extra-leading-parenthesis-whitespace', node=node, args=(')',))
