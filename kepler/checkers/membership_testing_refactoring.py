from libcst import Set as ConcreteSet
from libcst.matchers import extract, Comparison, ComparisonTarget, In, NotIn, Name, Integer, Arg, List, Tuple, SaveMatchedNode

from .base import BaseChecker


class MembershipTestingRefactoring(BaseChecker):
    NAME = 'membership_testing_refactoring'
    DESCRIPTION = 'Checks for refactoring of non-optimized membership testing.'
    OPTIONS = {}
    MESSAGES = {
        'faster-membership-testing': {
            'template': "Replace {!r} by {!r} as membership testing is faster with sets.",
            'description': """
            """,
        },
    }

    MATCHER = Comparison(
        comparisons=[
            ComparisonTarget(
                operator=In() | NotIn(),
                comparator=SaveMatchedNode(
                    List() | Tuple(),
                    'comparator'
                )
            )
        ]
    )

    def __init__(self):
        super().__init__()

    def visit_Comparison(self, node):
        match = extract(node, self.MATCHER)
        if match:
            comparator_node = match['comparator']
            new_node = ConcreteSet(elements=comparator_node.elements)

            self.add_error('faster-membership-testing', node=comparator_node, args=(comparator_node.code, new_node.code))
