import re

from .base import BaseChecker


class ClassNaming(BaseChecker):
    NAME = 'class_naming'
    DESCRIPTION = 'Checks the compliance of class names with the naming convention.'
    OPTIONS = {
        'style': {
            'default': 'pascal_case',
            'type': 'str',
            'metavar': 'NAME',
            'help': """
                The naming style to enforce.
            """,
        },
    }
    MESSAGES = {
        'invalid-class-name': {
            'template': "Class name {!r} not following {!r} convention.",
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

    def on_class(self, node):
        # ap(node.fst())

        if not re.match(self.CRE_FORMATS['pascal_case'], node.name):
            self.add_error('invalid-class-name', node=node, args=(node.name, 'pascal_case',))
