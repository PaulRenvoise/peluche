import re

from .base import BaseChecker


class ParenthesesSpacing(BaseChecker):
    NAME = 'parentheses_spacing'
    DESCRIPTION = 'Checks for correct spacing between parentheses.'
    OPTIONS = {}
    MESSAGES = {
        'missing-parenthesis-whitespace': {
            'template': "Missing whitespace before {!r}.",
            'description': """
            """,
        },
        'leading-parenthesis-whitespace': {
            'template': "Extraneous leading whitespace before {!r}.",
            'description': """
            """,
        },
        'trailing-parenthesis-whitespace': {
            'template': "Extraneous trailing whitespace after {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_class(self, node):
        # ap(node.fst())

        if node.parenthesis:
            if node.second_formatting.space:
                self.add_error('leading-parenthesis-whitespace', node=node.second_formatting.space, args=('(',))
            if node.third_formatting.space:
                self.add_error('trailing-parenthesis-whitespace', node=node.third_formatting.space, args=('(',))
            if node.fourth_formatting.space:
                self.add_error('leading-parenthesis-whitespace', node=node.fourth_formatting.space, args=(')',))

    def on_def(self, node):
        # ap(node.fst())

        if node.second_formatting.space:
            self.add_error('leading-parenthesis-whitespace', node=node.second_formatting.space, args=('(',))
        if node.third_formatting.space:
            self.add_error('trailing-parenthesis-whitespace', node=node.third_formatting.space, args=('(',))
        if node.fourth_formatting.space:
            self.add_error('leading-parenthesis-whitespace', node=node.fourth_formatting.space, args=(')',))

    def on_call(self, node):
        # ap(node.fst())

        if node.first_formatting.space:
            self.add_error('leading-parenthesis-whitespace', node=node.first_formatting.space, args=('(',))
        if node.second_formatting.space:
            self.add_error('trailing-parenthesis-whitespace', node=node.second_formatting.space, args=('(',))
        if node.third_formatting.space:
            self.add_error('leading-parenthesis-whitespace', node=node.third_formatting.space, args=(')',))

    def on_except(self, node):
        # ap(node.fst())

        if node.exception is not None and not node.first_formatting.space:
            self.add_error('missing-parenthesis-whitespace', node=node.first_formatting, args=('(',))

    def on_print(self, node):
        # ap(node.fst())

        if node.formatting.space:
            self.add_error('leading-parenthesis-whitespace', node=node.formatting.space, args=('(',))

    def on_associative_parenthesis(self, node):
        # ap(node.fst())

        if node.second_formatting.space:
            self.add_error('trailing-parenthesis-whitespace', node=node.second_formatting.space, args=('(',))
        if node.third_formatting.space:
            self.add_error('leading-parenthesis-whitespace', node=node.third_formatting.space, args=(')',))

    def on_tuple(self, node):
        # ap(node.fst())

        if not node.with_parenthesis:
            return

        if node.second_formatting.space:
            self.add_error('trailing-parenthesis-whitespace', node=node.second_formatting.space, args=('(',))
        # No trailing comma
        if node.third_formatting.space:
            self.add_error('leading-parenthesis-whitespace', node=node.third_formatting.space, args=(')',))
        elif len(node.value.node_list) > 0:
            last_value_node = node.value.node_list[-1]
            if last_value_node.type == 'comma':
                if last_value_node.second_formatting.space:
                    self.add_error('leading-parenthesis-whitespace', node=last_value_node.second_formatting.space, args=(')',))

