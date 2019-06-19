from .base import BaseChecker
from redbaron import SetNode


class MembershipTestingRefactoring(BaseChecker):
    NAME = 'membership_testing_refactoring'
    DESCRIPTION = 'Checks for refactoring of non-optimized membership testing.'
    OPTIONS = {}
    MESSAGES = {
        'faster-membership-testing': {
            'template': "Replace `{!r}` by `{!r}` as membership testing are faster with sets.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_comparison(self, node):
        # ap(node.fst())

        if node.value.first != 'in' and node.value.second != 'in':
            return

        if node.second.type in {'list', 'tuple'}:
            # TODO: would be better to have the following, but baron crashes
            # c.f. https://github.com/PyCQA/baron/issues/153
            # ```
            # new_node = SetNode({**node.second.fst(), 'type': 'set'})
            # ```
            new_fst = node.second.fst().copy()
            new_fst.update({'type': 'set'})
            new_node = SetNode(new_fst)

            self.add_error('faster-membership-testing', node=node, args=(node.second, new_node))

