from .base import BaseChecker


class CommaSpacing(BaseChecker):
    NAME = 'comma_spacing'
    DESCRIPTION = 'Checks the compliance with spacing rules around commas.'
    OPTIONS = {}
    MESSAGES = {
        'missing-comma-whitespace': {
            'template': "Missing whitespace after {!r}.",
            'description': """
            """,
        },
        'leading-comma-whitespace': {
            'template': "Extraneous leading whitespace before {!r}.",
            'description': """
            """,
        },
        'trailing-comma-whitespace': {
            'template': "Extraneous trailing whitespace after {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_comma(self, node):
        if len(node.first_formatting) > 0:
            self.add_error('leading-comma-whitespace', node=node, args=(',',))

        try:
            formatting = node.second_formatting[0]  # Raises IndexError if there is no formatting after the comma

            if formatting.type != 'endl':
                if formatting.value.startswith('  '):
                    self.add_error('trailing-comma-whitespace', node=node, args=(',',))
                elif formatting.value != ' ':
                    self.add_error('missing-comma-whitespace', node=node, args=(',',))
        except IndexError:
            # Tuples with one item are usually explicitly set with: `(item,)`
            if node.parent.type != 'tuple' or len(node.parent.value) > 1:
                self.add_error('missing-comma-whitespace', node=node, args=(',',))
