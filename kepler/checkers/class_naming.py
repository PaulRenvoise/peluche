import regex

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
        'snake_case': regex.compile(r"^[a-z\d_]+$"),
        'camel_case': regex.compile(r"^[a-z][a-zA-Z\d]+$"),
        'pascal_case': regex.compile(r"^[A-Z][a-zA-Z\d]+$"),
        'upper_case': regex.compile(r"^[A-Z\d_]+$"),
    }

    def __init__(self):
        super().__init__()

    def visit_ClassDef(self, node):
        if not self.CRE_FORMATS['pascal_case'].match(node.name.value):
            self.add_error('invalid-class-name', node=node.name, args=(node.name.value, 'pascal_case',))
