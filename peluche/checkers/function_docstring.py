from libcst.metadata import ScopeProvider, FunctionScope

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

    def visit_FunctionDef(self, node):
        # Do not enforce docstrings for private functions
        if node.name.value.startswith('_'):
            return

        # Also skip nested functions and closures
        scope = self.get_metadata(ScopeProvider, node)
        if isinstance(scope, FunctionScope):
            return

        docstring = node.get_docstring()

        if not docstring or docstring.strip() == '':
            self.add_error('missing-function-docstring', node=node, args=())
