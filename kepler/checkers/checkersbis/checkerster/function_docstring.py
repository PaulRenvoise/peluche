from .base import BaseChecker


class FunctionDocstring(BaseChecker):
    NAME = 'function_docstring'
    DESCRIPTION = 'Checks the presence of docstring for functions.'
    OPTIONS = {}
    MESSAGES = {
        'missing-function-docstring': {
            'template': "Function docstring is missing.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_def(self, node):
        # ap(node.fst())

        if getattr(node.scope, 'type', 'root') == 'def':
            return

        docstring = node.value.find('string')

        if not docstring or docstring.parent is not node:
            self.add_error('missing-function-docstring', node=node, args=())
