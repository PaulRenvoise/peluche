from libcst import Not, SimpleWhitespace

from .base import BaseChecker


class OperatorSpacing(BaseChecker):
    NAME = 'operator_spacing'
    DESCRIPTION = 'Checks for correct spacing around operators.'
    OPTIONS = {}
    MESSAGES = {
        'missing-leading-operator-whitespace': {
            'template': "Missing whitespace before {!r}.",
            'description': """
            """,
        },
        'missing-trailing-operator-whitespace': {
            'template': "Missing whitespace after {!r}.",
            'description': """
            """,
        },
        'extra-leading-operator-whitespace': {
            'template': "Extraneous whitespace before {!r}.",
            'description': """
            """,
        },
        'extra-trailing-operator-whitespace': {
            'template': "Extraneous whitespace after {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def visit_AssignTarget(self, node):
        leading = node.whitespace_before_equal.value
        if leading.startswith('  '):
            self.add_error('extra-leading-operator-whitespace', node=node, args=('=',))
        elif leading == '':
            self.add_error('missing-leading-operator-whitespace', node=node, args=('=',))

        trailing = node.whitespace_after_equal.value
        if trailing.startswith('  '):
            self.add_error('extra-trailing-operator-whitespace', node=node, args=('=',))
        elif trailing == '':
            self.add_error('missing-trailing-operator-whitespace', node=node, args=('=',))

    def visit_Comparison(self, node):
        for comparison in node.comparisons:
            self._check_spacing(comparison)

    def visit_BinaryOperation(self, node):
        self._check_spacing(node)

    def visit_BooleanOperation(self, node):
        self._check_spacing(node)

    def visit_UnaryOperation(self, node):
        operator_node = node.operator
        operator = operator_node._get_token()

        if isinstance(operator_node, Not):
            trailing = operator_node.whitespace_after.value

            if trailing.startswith('  '):
                self.add_error('extra-trailing-operator-whitespace', node=operator_node, args=(operator,))
            elif trailing == '':
                self.add_error('missing-trailing-operator-whitespace', node=operator_node, args=(operator,))
        else:
            trailing = operator_node.whitespace_after.value

            if trailing.startswith(' '):
                self.add_error('extra-trailing-operator-whitespace', node=operator_node, args=(operator,))

    def _check_spacing(self, node):
        operator_node = node.operator

        try:
            operator = operator_node.value
        except AttributeError:
            try:
                operator = operator_node._get_token()
            except AttributeError:
                operator = ' '.join(operator_node._get_tokens())

        whitespace_before_node = operator_node.whitespace_before
        if isinstance(whitespace_before_node, SimpleWhitespace):
            leading = whitespace_before_node.value
            if leading.startswith('  '):
                self.add_error('extra-leading-operator-whitespace', node=operator_node, args=(operator,))
            elif leading == '':
                self.add_error('missing-leading-operator-whitespace', node=operator_node, args=(operator,))
        else:
            leading = whitespace_before_node.first_line.whitespace.value
            if leading != '':
                self.add_error('extra-leading-operator-whitespace', node=operator_node, args=(operator,))

        whitespace_after_node = operator_node.whitespace_after
        if isinstance(whitespace_after_node, SimpleWhitespace):
            trailing = whitespace_after_node.value
            if trailing.startswith('  '):
                self.add_error('extra-trailing-operator-whitespace', node=operator_node, args=(operator,))
            elif trailing == '':
                self.add_error('missing-trailing-operator-whitespace', node=operator_node, args=(operator,))
        else:  # We have a carriage return after the operator
            trailing = whitespace_after_node.first_line.whitespace.value
            if trailing != '':
                self.add_error('extra-trailing-operator-whitespace', node=operator_node, args=(operator,))
