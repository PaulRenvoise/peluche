from .base import BaseChecker


class MinMaxRefactoring(BaseChecker):
    NAME = 'min_max_refactoring'
    DESCRIPTION = 'Checks for refactoring of non-optimized min/max value retrieval.'
    OPTIONS = {}
    MESSAGES = {
        'sorted-min': {
            'template': "Replace call to `{!r}` by `min()` as it is 1.2x faster.",
            'description': """
            """,
        },
        'sorted-max': {
            'template': "Replace call to `{!r}` by `max()` as it is 1.2x faster.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    # TODO: 'Checks for refactoring of `sorted(list)[0]` or `sorted(list][-1])` by `min()` or `max()`.'
    def on_atomtrailers(self, node):
        # ap(node.fst())

        pass
