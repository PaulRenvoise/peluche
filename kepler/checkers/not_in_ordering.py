from redbaron import ComparisonNode

from .base import BaseChecker


class NotInOrdering(BaseChecker):
    NAME = 'not_in_ordering'
    DESCRIPTION = 'Checks for compliance with the `not in` comparison convention.'
    OPTIONS = {}
    MESSAGES = {
        'misplaced-not': {
            'template': "Misplaced {!r} keyword, replace `{!r}` by `{!r}`.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_unitary_operator(self, node):
        if node.target.type != 'comparison':
            return

        if node.target.comparison_operator.first != 'in':
            return

        new_comparison_node = self._create_new_comparison_node(node.comparison.fst())

        self.add_error('misplaced-not', node=node, args=(node.value, node, new_comparison_node))

    def _create_new_comparison_node(self, fst):
        fst['value']['first'] = 'not'
        fst['value']['second'] = 'in'
        fst['value']['formatting'] = [{'type': 'space', 'value': ' '}]

        return ComparisonNode(fst)
