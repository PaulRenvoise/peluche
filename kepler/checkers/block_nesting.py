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
                Having blocks too nested reduces readability,
                and increases the difficulty to correctly test the function.
            """,
        },
    }

    NODES = {
        'def',
        'if',
        'while',
        'for',
        'try',
    }

    def __init__(self):
        super().__init__()

    def on_def(self, node):
        # ap(node.fst())

        # If we're processing a nested function, we ignore it
        # because we already processed the parent function
        if getattr(node.scope, 'type', 'root') == 'def':
            return

        self._compute_nesting(node, 3, -1)

    def _compute_nesting(self, node, max_nesting, current_nesting):
        if node.type in self.NODES:
            current_nesting += 1

            if current_nesting > max_nesting:
                self.add_error('block-too-nested', node=node, args=(current_nesting, max_nesting))
                return True

        for child in node.children:
            found = self._compute_nesting(child, max_nesting, current_nesting)
            if found:
                break
