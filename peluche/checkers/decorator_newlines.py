from .base import BaseChecker


class DecoratorNewlines(BaseChecker):
    NAME = 'decorator_newlines'
    DESCRIPTION = 'Checks the number of newlines after decorators.'
    OPTIONS = {
        'count': {
            'default': 1,
            'type': 'int',
            'metavar': 'COUNT',
            'help': """
                The maximum amount of newlines after a decorator.
            """,
        },
    }
    MESSAGES = {
        'extra-trailing-decorator-newline': {
            'template': "Extraneous newline after {!r} decorator.",
            'description': """
                TODO
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def visit_FunctionDef(self, node):
        if len(node.decorators) == 0:
            return

        prev_decorator_node = node.decorators[0]
        for decorator_node in node.decorators[1:]:
            if decorator_node.leading_lines:
                self.add_error('extra-trailing-decorator-newline', node=prev_decorator_node, args=(prev_decorator_node.decorator.value,))

            prev_decorator_node = decorator_node

        if node.lines_after_decorators:
            self.add_error('extra-trailing-decorator-newline', node=prev_decorator_node, args=(prev_decorator_node.decorator.value,))
