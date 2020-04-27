import isort

from .base import BaseChecker


class ImportOrdering(BaseChecker):
    NAME = 'import_ordering'
    DESCRIPTION = 'Checks the number of newlines between the import block and the following code.'
    OPTIONS = {
        'count': {
            'default': 2,
            'type': 'int',
            'metavar': 'COUNT',
            'help': """
                The enfored number of newlines.
            """,
        },
    }
    MESSAGES = {
        'missing-import-block-space': {
            'template': "Block is too nested within the function ({!r}/{!r}).",
            'description': """
                Having blocks too nested reduces readability,
                and increases the difficulty to correctly test the function.
            """,
        },
    }

    def __init__(self):
        self._isort = isort.SortImports(
            line_length=120,
            multi_line_output=3,
            indent=4,
            force_single_line=True,
            lines_after_imports=2,
        )
        super().__init__()

    def on_module(self, node):
        pass
