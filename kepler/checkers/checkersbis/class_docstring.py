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

    def on_class(self, node):
        # ap(node.fst())

        docstring = node.value.find('string')

        if not docstring or docstring.parent is not node:
            self.add_error('missing-class-docstring', node=node, args=())
