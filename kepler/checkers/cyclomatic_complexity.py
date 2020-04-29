from libcst.matchers import findall, OneOf
from libcst.matchers import Try, For, While, CompFor, If, Assert, BooleanOperation, IfExp

from .base import BaseChecker


class CyclomaticComplexity(BaseChecker):
    NAME = 'cyclomatic_complexity'
    DESCRIPTION = 'Checks the maximum cyclomatic complexity of functions.'
    OPTIONS = {
        'max': {
            'default': 10,
            'type': 'int',
            'metavar': 'COMPLEXITY',
            'help': """
                The maximum cyclomatic complexity.
            """,
        },
    }
    MESSAGES = {
        'function-too-complex': {
            'template': "Function is too complex ({!r}/{!r}).",
            'description': """
            """,
        },
    }

    NODES = (
        Try(),
        For(),
        While(),
        CompFor(),
        If(),
        Assert(),
        BooleanOperation(),
        IfExp(),
    )

    def __init__(self):
        super().__init__()

    def visit_FunctionDef(self, node):
        complexity = 1

        for child_node in findall(node, OneOf(*self.NODES)):
            class_name = child_node.__class__.__name__

            if class_name == 'Try':
                complexity += len(child_node.handlers) + bool(child_node.orelse)
            elif class_name == 'BooleanOperation':
                complexity += 1
            elif class_name in {'If', 'IfExp', 'Assert'}:
                complexity += 1
            elif class_name in {'For', 'While'}:
                complexity += bool(child_node.orelse) + 1
            elif class_name == 'CompFor':
                complexity += len(child_node.ifs) + 1

        if complexity > 10:
            self.add_error('function-too-complex', node=node, args=(complexity, 10))
