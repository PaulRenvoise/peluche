from .base import BaseChecker


class ModuleNewlines(BaseChecker):
    NAME = 'module_newlines'
    DESCRIPTION = 'Checks the number of newlines after modules.'
    OPTIONS = {}
    MESSAGES = {
        'missing-trailing-module-newline': {
            'template': "Missing newline after module.",
            'description': """
                TODO
            """,
        },
        'extra-trailing-module-newline': {
            'template': "Extraneous newline after module.",
            'description': """
                TODO
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def visit_Module(self, node):
        if not node.has_trailing_newline:
            self.add_error('missing-trailing-module-newline', node=node, args=())
        else:
            if node.footer:
                self.add_error('extra-trailing-module-newline', node=node, args=())
