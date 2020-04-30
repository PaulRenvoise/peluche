from .base import BaseChecker


class ClassDocstring(BaseChecker):
    NAME = 'class_docstring'
    DESCRIPTION = 'Checks the presence of docstring for classes.'
    OPTIONS = {}
    MESSAGES = {
        'missing-class-docstring': {
            'template': "Class docstring is missing.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def visit_ClassDef(self, node):
        docstring = node.get_docstring()

        if not docstring or docstring.strip() == '':
            self.add_error('missing-class-docstring', node=node, args=())
