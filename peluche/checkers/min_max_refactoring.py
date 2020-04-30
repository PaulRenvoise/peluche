from libcst import Call as ConcreteCall, Name as ConcreteName, Arg as ConcreteArg
from libcst.metadata import ParentNodeProvider
from libcst.matchers import extract, OneOf, ZeroOrOne, SaveMatchedNode, Subscript, Call, Name, SubscriptElement, Index, UnaryOperation, Integer, Arg, Minus

from .base import BaseChecker


class MinMaxRefactoring(BaseChecker):
    NAME = 'min_max_refactoring'
    DESCRIPTION = 'Checks for refactoring of non-optimized min/max value retrieval.'
    OPTIONS = {}
    MESSAGES = {
        'sorted-min': {
            'template': "Replace call to {!r} by {!r} as it is 1.2x faster.",
            'description': """
                min() is faster than sorted() because it only needs to traverse the list once.
            """,
        },
        'sorted-max': {
            'template': "Replace call to {!r} by {!r} as it is 1.2x faster.",
            'description': """
                max() is faster than sorted() because it only needs to traverse the list once.
            """,
        },
    }

    MATCHER = Subscript(
        value=Call(
            func=Name('sorted'),
            args=(
                SaveMatchedNode(
                    Arg(),
                    'arg'
                ),
                ZeroOrOne(
                    SaveMatchedNode(
                        Arg(
                            value=Name('True'),
                            keyword=Name('reverse')
                        ),
                        'kwarg'
                    )
                )
            )
        ),
        slice=[
            SubscriptElement(
                slice=Index(
                    value=SaveMatchedNode(
                        OneOf(
                            UnaryOperation(
                                operator=Minus(),
                                expression=Integer(
                                    value='1'
                                )
                            ),
                            Integer(
                                value='0'
                            )
                        ),
                        'index',
                    )
                ),
            )
        ]
    )

    def __init__(self):
        super().__init__()

    def visit_Subscript(self, node):
        match = extract(node, self.MATCHER)
        if match:
            # Even though we defined two matchers (one for arg, and the other for kwargs),
            # when kwarg is present, it also ends up in arg
            arg_node = match['arg'][0]
            index_node = match['index']

            # Instead of handling the UnaryOperation and the Integer case differently
            # we just convert them to code and check their value
            index = index_node.code
            if index == '0':
                func_name = 'min'
            elif index == '-1':
                func_name = 'max'

            # If we have a kwarg, it must be 'reverse=True' because of the matcher,
            # thus we reverse the suggestion
            if 'kwarg' in match:
                func_name = 'max' if func_name == 'min' else 'min'

            new_node = ConcreteCall(func=ConcreteName(func_name), args=(ConcreteArg(value=arg_node.value),))

            self.add_error(f"sorted-{func_name}", node=node, args=(node.code, new_node.code))
