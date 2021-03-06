from libcst.matchers import extract, Call, Name, Integer, Arg, SaveMatchedNode, OneOf

from .base import BaseChecker


class EnumerateRefactoring(BaseChecker):
    NAME = 'enumerate_refactoring'
    DESCRIPTION = 'Checks for refactoring of non-optimized enumerations.'
    OPTIONS = {}
    MESSAGES = {
        'range-enumerate': {
            'template': "Replace call to {!r} by 'enumerate({})'.",
            'description': """
            """,
        },
    }


    # Matches 'range(len(...))' and 'range(0, len(...))' and captures the call to 'len'
    MATCHER = Call(
        func=Name('range'),
        args=OneOf(
            (
                Arg(
                    SaveMatchedNode(
                        Call(
                            func=Name(value='len')
                        ),
                        'call'
                    )
                ),
            ),
            (
                Arg(
                    Integer(
                        value='0'
                    )
                ),
                Arg(
                    SaveMatchedNode(
                        Call(
                            func=Name(value='len')
                        ),
                        'call'
                    )
                )
            )
        )
    )

    def __init__(self):
        super().__init__()

    def visit_For(self, node):
        match = extract(node.iter, self.MATCHER)
        if match:
            arg_node = match['call'].args[0].value
            self.add_error('range-enumerate', node=node.iter, args=(node.iter.code, arg_node.code))
