from .base import BaseChecker


# TODO
class FunctionNewlines(BaseChecker):
    NAME = 'function_newlines'
    DESCRIPTION = 'Checks the number of newlines after functions.'
    OPTIONS = {
        'count': {
            'default': 2,
            'type': 'int',
            'metavar': 'DEPTH',
            'help': """
                The maximum amount of newlines after a function.
            """,
        },
    }
    MESSAGES = {
        'missing-newlines-after-function': {
            'template': "Missing newline after {!r} function.",
            'description': """
                TODO
            """,
        },
        'trailing-newlines-after-function': {
            'template': "Extraneous trailing newline after {!r} function.",
            'description': """
                TODO
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_def(self, node):
        # If we're processing a nested function, we ignore it
        scope = getattr(node.scope, 'type', 'root')
        if scope == 'def':
            return
        elif scope == 'class':  # Methods = 1 newline
            self._check_newlines(node, count=1)
        elif scope == 'root':  # Functions = 2 newlines
            self._check_newlines(node, count=2)

    def _check_newlines(self, node, count=0):
        pass
