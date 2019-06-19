from .base import BaseChecker


class LineLength(BaseChecker):
    NAME = 'line_length'
    DESCRIPTION = 'Checks the maximum line length.'
    OPTIONS = {
        'max': {
            'default': 120,
            'type': 'int',
            'metavar': 'LENGTH',
            'help': """
                The maximum length allowed.
            """,
        },
        'ignore-docstrings': {  # TODO
            'default': True,
            'type': 'bool',
            'metavar': 'TRUE or FALSE',
            'help': """
                Whether or not to ignore docstrings.
            """
        },
        'ignore-comments': {  # TODO
            'default': True,
            'type': 'bool',
            'metavar': 'TRUE or FALSE',
            'help': """
                Whether or not to ignore comments.
            """
        },
        'ignore-uris': {  # TODO
            'default': True,
            'type': 'bool',
            'metavar': 'TRUE or FALSE',
            'help': """
                Whether or not to ignore URIs.
            """
        },
    }
    MESSAGES = {
        'line-too-long': {
            'template': "Line is too long ({!r}/{!r}).",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_module(self, node):
        # ap(node.fst())
        raw = node.dumps()

        for index, line in enumerate(raw.split('\n'), start=1):
            if not line:
                continue

            line_len = len(line)
            if line_len > 120:
                self.add_error('line-too-long', node=node.at(index), args=(line_len, 120))
