from libcst import If, While, For, Try, FunctionDef
from libcst.metadata import ScopeProvider, FunctionScope

from .base import BaseChecker


class BlockNesting(BaseChecker):
    NAME = 'block_nesting'
    DESCRIPTION = 'Checks the maximum nesting of code blocks.'
    OPTIONS = {
        'max': {
            'default': 3,
            'type': 'int',
            'metavar': 'DEPTH',
            'help': """
                The maximum nesting allowed.
            """,
        },
    }
    MESSAGES = {
        'block-too-nested': {
            'template': "Block is too nested within the function ({!r}/{!r}).",
            'description': """
                Having blocks too deeply nested reduces readability,
                and increases the difficulty to correctly test the function.
            """,
        },
    }

    NESTABLE_NODES = (
        FunctionDef,
        If,
        While,
        For,
        Try,
    )

    def __init__(self):
        super().__init__()

    def visit_FunctionDef(self, node):
        scope = self.get_metadata(ScopeProvider, node)
        # If we're processing a nested function, we ignore it
        # because we already processed the parent function
        if isinstance(scope, FunctionScope):
            return

        self._check_nesting(node, 3, -1)

    def _check_nesting(self, node, max_nesting, current_nesting):
        if isinstance(node, self.NESTABLE_NODES):
            current_nesting += 1

            if current_nesting > max_nesting:
                self.add_error('block-too-nested', node=node, args=(current_nesting, max_nesting))
                return True

        for child in node.children:
            found = self._check_nesting(child, max_nesting, current_nesting)
            if found:
                break
