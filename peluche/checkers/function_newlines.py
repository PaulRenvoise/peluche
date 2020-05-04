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
        scope = self.get_metadata(ScopeProvider, node)
        if isinstance(scope, (FunctionScope, ClassScope)):
            offset = 1
        elif isinstance(scope, GlobalScope):
            offset = 2

        parent_node = self.get_metadata(ParentNodeProvider, node)
        parent_position = self.get_metadata(PositionProvider, parent_node)
        position = self.get_metadata(PositionProvider, node)
        # A module is actually counted as one line longer than it is,
        # so we use offset to take that in account
        # This gives us '+ 0' for functions and classes
        # and '+ 1' for modules
        if position.end.line + (offset - 1) == parent_position.end.line:
            return

        # Finds true empty lines (no comments) following the function
        matcher = EmptyLine(
            comment=None,
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
