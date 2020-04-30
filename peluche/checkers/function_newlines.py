from libcst.matchers import findall, MatchMetadataIfTrue, EmptyLine
from libcst.metadata import ParentNodeProvider, PositionProvider, ScopeProvider, GlobalScope, ClassScope, FunctionScope

from .base import BaseChecker


class FunctionNewlines(BaseChecker):
    NAME = 'function_newlines'
    DESCRIPTION = 'Checks the number of newlines after functions.'
    OPTIONS = {
        'count': {
            'default': 2,
            'type': 'int',
            'metavar': 'DEPTH',
            'help': """
                The maximum amount of newlines after a function.
            """,
        },
    }
    MESSAGES = {
        'missing-trailing-function-newline': {
            'template': "Missing newline after {!r} function.",
            'description': """
                TODO
            """,
        },
        'extra-trailing-function-newline': {
            'template': "Extraneous trailing newline after {!r} function.",
            'description': """
                TODO
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def visit_FunctionDef(self, node):
        end_line = len(self.source.lines)
        position = self.get_metadata(PositionProvider, node)
        if position.end.line == end_line:
            return

        parent_node = self.get_metadata(ParentNodeProvider, node)

        scope = self.get_metadata(ScopeProvider, node)
        if isinstance(scope, (FunctionScope, ClassScope)):
            offset = 1
        elif isinstance(scope, GlobalScope):
            offset = 2

        matcher = EmptyLine(
            metadata=MatchMetadataIfTrue(
                PositionProvider,
                lambda p: position.end.line < p.start.line <= position.end.line + offset + 1

            )
        )
        nodes_count = len(findall(parent_node, matcher, metadata_resolver=self))

        if nodes_count > offset:
            self.add_error('extra-trailing-function-newline', node=node, args=(node.name.value,))
        elif nodes_count < offset:
            self.add_error('missing-trailing-function-newline', node=node, args=(node.name.value,))
