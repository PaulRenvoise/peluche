from libcst import SimpleWhitespace
from libcst.matchers import findall, MatchMetadataIfTrue, RightCurlyBrace
from libcst.metadata import PositionProvider, ParentNodeProvider

from .base import BaseChecker


class BraceSpacing(BaseChecker):
    NAME = 'brace_spacing'
    DESCRIPTION = 'Checks for correct spacing between braces.'
    OPTIONS = {}
    MESSAGES = {
        'missing-leading-brace-whitespace': {
            'template': "Missing whitespace before {!r}.",
            'description': """
            """,
        },
        'extra-leading-brace-whitespace': {
            'template': "Extraneous whitespace before {!r}.",
            'description': """
            """,
        },
        'extra-trailing-brace-whitespace': {
            'template': "Extraneous whitespace after {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def visit_LeftCurlyBrace(self, node):
        whitespace_after_node = node.whitespace_after
        if isinstance(whitespace_after_node, SimpleWhitespace):
            if whitespace_after_node.value != '':
                self.add_error('extra-trailing-brace-whitespace', node=node, args=('{',))
        else:
            trailing = whitespace_after_node.first_line.whitespace.value
            if trailing != '':
                self.add_error('extra-trailing-brace-whitespace', node=node, args=('{',))


    def visit_RightCurlyBrace(self, node):
        whitespace_before_node = node.whitespace_before
        if isinstance(whitespace_before_node, SimpleWhitespace):
            if whitespace_before_node.value != '':
                self.add_error('extra-leading-brace-whitespace', node=node, args=('}',))
        else:
            leading = whitespace_before_node.first_line.whitespace.value
            if leading != '':
                self.add_error('extra-leading-brace-whitespace', node=node, args=('}',))

    # We prefer to check if a TrailingWhitespace follows a RightCurlyBrace
    # rather than check if a RightCurlyBrace is followed by a TrailingWhiteSpace
    # because a TrailingWhitespace tends to appear less often than a RightCurlyBrace in code
    def visit_TrailingWhitespace(self, node):
        if node.comment is not None:
            return
        if node.whitespace.value == '':
            return

        position = self.get_metadata(PositionProvider, node)
        parent_node = self.get_metadata(ParentNodeProvider, node)

        matcher = RightCurlyBrace(
            metadata=MatchMetadataIfTrue(
                PositionProvider,
                lambda p: position.start.line == p.start.line and position.start.column == p.end.column
            )
        )
        matches = findall(parent_node, matcher, metadata_resolver=self)
        if matches:
            self.add_error('extra-trailing-brace-whitespace', node=matches[0], args=('}',))
