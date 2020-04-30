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

    def visit_FunctionDef(self, node):
        if not self.CRE_FORMATS['snake_case'].match(node.name.value):
            self.add_error('invalid-function-name', node=node.name, args=(node.name.value, 'snake_case'))
