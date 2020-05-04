from libcst import SimpleWhitespace
from libcst.matchers import findall, MatchMetadataIfTrue, RightSquareBracket
from libcst.metadata import PositionProvider, ParentNodeProvider

from .base import BaseChecker


class BracketSpacing(BaseChecker):
    NAME = 'bracket_spacing'
    DESCRIPTION = 'Checks for correct spacing between brackets.'
    OPTIONS = {}
    MESSAGES = {
        'missing-leading-bracket-whitespace': {
            'template': "Missing whitespace before {!r}.",
            'description': """
            """,
        },
        'extra-leading-bracket-whitespace': {
            'template': "Extraneous whitespace before {!r}.",
            'description': """
            """,
        },
        'extra-trailing-bracket-whitespace': {
            'template': "Extraneous whitespace after {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def visit_LeftSquareBracket(self, node):
        whitespace_after_node = node.whitespace_after
        if isinstance(whitespace_after_node, SimpleWhitespace):
            if whitespace_after_node.value != '':
                self.add_error('extra-trailing-bracket-whitespace', node=node, args=('[',))
        else:
            first_line_node = whitespace_after_node.first_line
            if first_line_node.comment is not None:
                return

            if first_line_node.whitespace.value != '':
                self.add_error('extra-trailing-bracket-whitespace', node=node, args=('[',))

    def visit_RightSquareBracket(self, node):
        whitespace_before_node = node.whitespace_before
        if isinstance(whitespace_before_node, SimpleWhitespace):
            if whitespace_before_node.value != '':
                self.add_error('extra-leading-bracket-whitespace', node=node, args=(']',))
        else:
            first_line_node = whitespace_before_node.first_line
            if first_line_node.comment is not None:
                return

            if first_line_node.whitespace.value != '':
                self.add_error('extra-leading-bracket-whitespace', node=node, args=(']',))

    # We prefer to check if a TrailingWhitespace follows a RightSquareBracket
    # rather than check if a RightSquareBracket is followed by a TrailingWhiteSpace
    # because a TrailingWhitespace tends to appear less often than a RightSquareBracket in code
    def visit_TrailingWhitespace(self, node):
        if node.comment is not None:
            return
        if node.whitespace.value == '':
            return

        position = self.get_metadata(PositionProvider, node)
        parent_node = self.get_metadata(ParentNodeProvider, node)

        matcher = RightSquareBracket(
            metadata=MatchMetadataIfTrue(
                PositionProvider,
                lambda p: position.start.line == p.start.line and position.start.column == p.end.column
            )
        )
        matches = findall(parent_node, matcher, metadata_resolver=self)
        if matches:
            self.add_error('extra-trailing-bracket-whitespace', node=matches[0], args=(']',))
