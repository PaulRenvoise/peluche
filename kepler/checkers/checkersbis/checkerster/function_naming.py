import re

from .base import BaseChecker


class FunctionNaming(BaseChecker):
    NAME = 'function_naming'
    DESCRIPTION = 'Checks the compliance of function names with the naming convention.'
    OPTIONS = {
        'format': {
            'default': 'snake_case',
            'type': 'str',
            'metavar': 'FORMAT',
            'help': """
                The naming style to enforce.
            """,
        },
    }
    MESSAGES = {
        'invalid-function-name': {
            'template': "Function name {!r} not following {!r} convention.",
            'description': """
                Following a unique naming style across all the codebase helps readability.
            """,
        },
    }

    CRE_FORMATS = {
        'snake_case': re.compile(r"^[a-z\d_]+$"),
        'camel_case': re.compile(r"^[a-z][a-zA-Z\d]+$"),
        'pascal_case': re.compile(r"^[A-Z][a-zA-Z\d]+$"),
        'upper_case': re.compile(r"^[A-Z\d_]+$"),
    }

    def __init__(self):
        super().__init__()

    def on_def(self, node):
        # ap(node.fst())

        if not re.match(self.CRE_FORMATS['snake_case'], node.name):
            self.add_error('invalid-function-name', node=node, args=(node.name, 'snake_case',))
