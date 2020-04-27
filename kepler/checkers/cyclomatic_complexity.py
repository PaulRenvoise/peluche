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

    # All those nodes count for 1 in the cyclomatic complexity
    # The elses from the fors, whiles, and try/excepts are caught as standard elses
    SIMPLE_NODES = {
        'def',
        'lambda',
        'decorator',
        'with',
        'try',
        'except',
        'finally',
        'for',
        'while',
        'comprehension_loop',
        'if',
        'elif',
        'else',
        'comprehension_if',
        'assert',
        'boolean_operator'
    }
    # Ternary operators are equivalent to an if/else
    DOUBLE_NODES = {'ternary_operator'}
    # Interval comparisons are just syntax sugar for two comparisons with a boolean operator in-between
    POSSIBLE_NODES = {'comparison'}

    # We can't use sets for `.find_all()` to work correctly...
    NODES = tuple(SIMPLE_NODES | DOUBLE_NODES | POSSIBLE_NODES)

    def __init__(self):
        super().__init__()

    def on_def(self, node):
        complexity = 0

        for single_node in node.find_all(self.NODES):
            single_node_type = single_node.type

            if single_node_type in self.SIMPLE_NODES:
                complexity += 1
            elif single_node_type in self.DOUBLE_NODES:
                complexity += 2
            elif single_node_type in self.POSSIBLE_NODES:
                if single_node_type == 'comparison' and single_node.second.type == 'comparison':
                    complexity += 1

        if complexity > 10:
            self.add_error('function-too-complex', node=node, args=(complexity, 10))
