from .base import BaseChecker


class OperatorSpacing(BaseChecker):
    NAME = 'operator_spacing'
    DESCRIPTION = 'Checks for correct spacing around operators.'
    OPTIONS = {}
    MESSAGES = {
        'missing-operator-whitespace': {
            'template': "Missing whitespace around {!r}.",
            'description': """
            """,
        },
        'leading-operator-whitespace': {
            'template': "Extraneous leading whitespace before {!r}.",
            'description': """
            """,
        },
        'trailing-operator-whitespace': {
            'template': "Extraneous trailing whitespace after {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_assignment(self, node):
        self._check_spacing(node, operator=node.operator + '=')

    def on_comparison(self, node):
        self._check_spacing(node, operator=node.value.first)

    def on_binary_operator(self, node):
        self._check_spacing(node, operator=node.value)

    def on_boolean_operator(self, node):
        self._check_spacing(node, operator=node.value)

    def on_unitary_operator(self, node):
        operator = node.value

        if operator == 'not':
            try:
                formatting = node.formatting[0]

                if getattr(formatting, 'value', '').startswith('  '):
                    self.add_error('trailing-operator-whitespace', node=node, args=(operator,))
                elif getattr(formatting, 'value', '')[0] != ' ':
                    self.add_error('missing-operator-whitespace', node=node, args=(operator,))
            except IndexError:
                self.add_error('missing-operator-whitespace', node=node, args=(operator,))
        else:
            try:
                formatting = node.formatting[0]

                if getattr(formatting, 'value', '')[0] == ' ':
                    self.add_error('trailing-operator-whitespace', node=node, args=(operator,))
            except IndexError:
                pass

    def _check_spacing(self, node, operator=None):
        try:
            formatting = node.first_formatting[0]
            if getattr(formatting, 'value', '').startswith('  '):
                self.add_error('leading-operator-whitespace', node=node, args=(operator,))
            elif getattr(formatting, 'value', '')[0] != ' ':
                self.add_error('missing-operator-whitespace', node=node, args=(operator,))

            formatting = node.second_formatting[0]
            if getattr(formatting, 'value', '').startswith('  '):
                self.add_error('trailing-operator-whitespace', node=node, args=(operator,))
            elif getattr(formatting, 'value', '')[0] != ' ':
                self.add_error('missing-operator-whitespace', node=node, args=(operator,))
        except IndexError:
            self.add_error('missing-operator-whitespace', node=node, args=(operator,))
