from libcst import NotIn
from libcst import ComparisonTarget as ConcreteComparisonTarget
from libcst import Comparison as ConcreteComparison
from libcst.matchers import extract, UnaryOperation, Comparison, ComparisonTarget, In, Not, DoNotCare, SaveMatchedNode

from .base import BaseChecker


class NotInRefactoring(BaseChecker):
    NAME = 'not_in_refactoring'
    DESCRIPTION = 'Checks for compliance with the `not in` comparison convention.'
    OPTIONS = {}
    MESSAGES = {
        'misplaced-not': {
            'template': "Misplaced {!r} keyword, replace {!r} by {!r}.",
            'description': """
            """,
        },
    }

    MATCHER = UnaryOperation(
        operator=Not(),
        expression=Comparison(
            left=SaveMatchedNode(
                DoNotCare(),
                'left'
            ),
            comparisons=[
                ComparisonTarget(
                    operator=In(),
                    comparator=SaveMatchedNode(
                        DoNotCare(),
                        'comparator'
                    )
                )
            ]
        )
    )

    def __init__(self):
        super().__init__()

    def visit_UnaryOperation(self, node):
        match = extract(node, self.MATCHER)
        if match:
            left_node = match['left']
            comparator_node = match['comparator']
            new_node = ConcreteComparison(left=left_node, comparisons=[ConcreteComparisonTarget(operator=NotIn(), comparator=comparator_node)])

            self.add_error('misplaced-not', node=node, args=('not', node.code, new_node.code))
