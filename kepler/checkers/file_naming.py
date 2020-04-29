import regex

from .base import BaseChecker


class FileNaming(BaseChecker):
    NAME = 'file_naming'
    DESCRIPTION = 'Checks the compliance of file names with the naming convention.'
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
        'invalid-file-name': {
            'template': "File name {!r} not following {!r} convention.",
            'description': """
                Following a unique naming style across all the codebase helps readability.
            """,
        }
    }

    CRE_FORMATS = {
        'snake_case': regex.compile(r"^[a-z\d_]+$"),
        'camel_case': regex.compile(r"^[a-z][a-zA-Z\d]+$"),
        'pascal_case': regex.compile(r"^[A-Z][a-zA-Z\d]+$"),
        'upper_case': regex.compile(r"^[A-Z\d_]+$"),
    }

    def __init__(self):
        super().__init__()

    def visit_Module(self, _node):
        if not self.CRE_FORMATS['snake_case'].match(self.source.basename):
            self.add_error('invalid-file-name', position=(0, 0), args=(self.source.filename, 'snake_case'))
