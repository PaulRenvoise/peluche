from .base import BaseChecker


class DecoratorNewlines(BaseChecker):
    NAME = 'decorator_newlines'
    DESCRIPTION = 'Checks the number of newlines after decorators.'
    OPTIONS = {
        'count': {
            'default': 1,
            'type': 'int',
            'metavar': 'COUNT',
            'help': """
                The maximum amount of newlines after a decorator.
            """,
        },
    }
    MESSAGES = {
        'trailing-decorator-newline': {
            'template': "Extraneous trailing newline after {!r} decorator.",
            'description': """
                TODO
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_def(self, node):
        if len(node.decorators) == 0:
            return

        # We MUST have a decorator somewhere, else we won't even reach this part
        decorator_node = node.decorators[0]
        for item in node.decorators[1:]:
            if item.type == 'decorator':
                decorator_node = item
                endl_count = 1
            elif item.type == 'endl':
                endl_count += 1

            if endl_count > 1:
                self.add_error('trailing-decorator-newline', node=decorator_node, args=(decorator_node.dumps(),))
