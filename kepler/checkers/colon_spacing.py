from libcst import LeftParen, RightParen, Colon

from .base import BaseChecker


class ColonSpacing(BaseChecker):
    NAME = 'colon_spacing'
    DESCRIPTION = 'Checks the compliance with spacing rules around colons.'
    OPTIONS = {}
    MESSAGES = {
        'missing-trailing-colon-whitespace': {
            'template': "Missing whitespace after {!r}.",
            'description': """
            """,
        },
        'extra-leading-colon-whitespace': {
            'template': "Extraneous whitespace before {!r}.",
            'description': """
            """,
        },
        'extra-trailing-colon-whitespace': {
            'template': "Extraneous whitespace after {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def visit_ClassDef(self, node):
        # With parenthesis
        if isinstance(node.lpar, LeftParen) and isinstance(node.rpar, RightParen):
            leading = node.whitespace_before_colon.value
            if leading != '':
                self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))
        else:
            leading = node.whitespace_after_name.value
            if leading != '':
                self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))

        try:
            trailing = node.body.header.whitespace.value
            # If we have a comment, the spaces "belong" to the comment
            # TODO: link to comments's checker
            if not node.body.header.comment and trailing != '':
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
        except AttributeError:  # We don't have a IndentedBlock: we're in a one-liner
            trailing = node.body.leading_whitespace.value
            if trailing.startswith('  '):
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
            elif trailing != ' ':
                self.add_error('missing-trailing-colon-whitespace', node=node, args=(':',))

    def visit_FunctionDef(self, node):
        leading = node.whitespace_before_colon.value
        if leading != '':
            self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))

        try:
            trailing = node.body.header.whitespace.value
            # If we have a comment, the spaces "belong" to the comment
            # TODO: link to comments's checker
            if not node.body.header.comment and trailing != '':
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
        except AttributeError:  # We don't have a IndentedBlock: we're in a one-liner
            trailing = node.body.leading_whitespace.value
            if trailing.startswith('  '):
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
            elif trailing != ' ':
                self.add_error('missing-trailing-colon-whitespace', node=node, args=(':',))

    def visit_Lambda(self, node):
        # With parameters
        if node.params.params:
            leading = node.params.params[-1].whitespace_after_param.value
            if leading != '':
                self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))
        else:
            leading = node.colon.whitespace_before.value
            if leading != '':
                self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))

        trailing = node.colon.whitespace_after.value
        if trailing.startswith('  '):
            self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
        elif trailing != ' ':
            self.add_error('missing-trailing-colon-whitespace', node=node, args=(':',))

    # Handles both if and elif keywords
    def visit_If(self, node):
        leading = node.whitespace_after_test.value
        if leading != '':
            self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))

        try:
            trailing = node.body.header.whitespace.value
            # If we have a comment, the spaces "belong" to the comment
            # TODO: link to comments's checker
            if not node.body.header.comment and trailing != '':
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
        except AttributeError:  # We don't have a IndentedBlock: we're in a one-liner
            trailing = node.body.leading_whitespace.value
            if trailing.startswith('  '):
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
            elif trailing != ' ':
                self.add_error('missing-trailing-colon-whitespace', node=node, args=(':',))

    def visit_Else(self, node):
        leading = node.whitespace_before_colon.value
        if leading != '':
            self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))

        try:
            trailing = node.body.header.whitespace.value
            # If we have a comment, the spaces "belong" to the comment
            # TODO: link to comments's checker
            if not node.body.header.comment and trailing != '':
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
        except AttributeError:  # We don't have a IndentedBlock: we're in a one-liner
            trailing = node.body.leading_whitespace.value
            if trailing.startswith('  '):
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
            elif trailing != ' ':
                self.add_error('missing-trailing-colon-whitespace', node=node, args=(':',))

    def visit_With(self, node):
        leading = node.whitespace_before_colon.value
        if leading != '':
            self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))

        try:
            trailing = node.body.header.whitespace.value
            # If we have a comment, the spaces "belong" to the comment
            # TODO: link to comments's checker
            if not node.body.header.comment and trailing != '':
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
        except AttributeError:  # We don't have a IndentedBlock: we're in a one-liner
            trailing = node.body.leading_whitespace.value
            if trailing.startswith('  '):
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
            elif trailing != ' ':
                self.add_error('missing-trailing-colon-whitespace', node=node, args=(':',))

    def visit_Try(self, node):
        leading = node.whitespace_before_colon.value
        if leading != '':
            self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))

        try:
            trailing = node.body.header.whitespace.value
            # If we have a comment, the spaces "belong" to the comment
            # TODO: link to comments's checker
            if not node.body.header.comment and trailing != '':
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
        except AttributeError:  # We don't have a IndentedBlock: we're in a one-liner
            trailing = node.body.leading_whitespace.value
            if trailing.startswith('  '):
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
            elif trailing != ' ':
                self.add_error('missing-trailing-colon-whitespace', node=node, args=(':',))

    def visit_ExceptHandler(self, node):
        leading = node.whitespace_before_colon.value
        if leading != '':
            self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))

        try:
            trailing = node.body.header.whitespace.value
            # If we have a comment, the spaces "belong" to the comment
            # TODO: link to comments's checker
            if not node.body.header.comment and trailing != '':
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
        except AttributeError:  # We don't have a IndentedBlock: we're in a one-liner
            trailing = node.body.leading_whitespace.value
            if trailing.startswith('  '):
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
            elif trailing != ' ':
                self.add_error('missing-trailing-colon-whitespace', node=node, args=(':',))

    def visit_Finally(self, node):
        leading = node.whitespace_before_colon.value
        if leading != '':
            self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))

        try:
            trailing = node.body.header.whitespace.value
            # If we have a comment, the spaces "belong" to the comment
            # TODO: link to comments's checker
            if not node.body.header.comment and trailing != '':
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
        except AttributeError:  # We don't have a IndentedBlock: we're in a one-liner
            trailing = node.body.leading_whitespace.value
            if trailing.startswith('  '):
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
            elif trailing != ' ':
                self.add_error('missing-trailing-colon-whitespace', node=node, args=(':',))

    def visit_For(self, node):
        leading = node.whitespace_before_colon.value
        if leading != '':
            self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))

        try:
            trailing = node.body.header.whitespace.value
            # If we have a comment, the spaces "belong" to the comment
            # TODO: link to comments's checker
            if not node.body.header.comment and trailing != '':
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
        except AttributeError:  # We don't have a IndentedBlock: we're in a one-liner
            trailing = node.body.leading_whitespace.value
            if trailing.startswith('  '):
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
            elif trailing != ' ':
                self.add_error('missing-trailing-colon-whitespace', node=node, args=(':',))

    def visit_While(self, node):
        leading = node.whitespace_before_colon.value
        if leading != '':
            self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))

        try:
            trailing = node.body.header.whitespace.value
            # If we have a comment, the spaces "belong" to the comment
            # TODO: link to comments's checker
            if not node.body.header.comment and trailing != '':
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
        except AttributeError:  # We don't have a IndentedBlock: we're in a one-liner
            trailing = node.body.leading_whitespace.value
            if trailing.startswith('  '):
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
            elif trailing != ' ':
                self.add_error('missing-trailing-colon-whitespace', node=node, args=(':',))

    def visit_DictElement(self, node):
        leading = node.whitespace_before_colon.value
        if leading != '':
            self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))

        trailing = node.whitespace_after_colon.value
        if trailing.startswith('  '):
            self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
        elif trailing != ' ':
            self.add_error('missing-trailing-colon-whitespace', node=node, args=(':',))

    # TODO: should we follow: https://www.python.org/dev/peps/pep-0008/#whitespace-in-expressions-and-statements ?
    def visit_Slice(self, node):
        first_colon = node.first_colon
        if first_colon.whitespace_before.value != '':
            self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))
        if first_colon.whitespace_after.value != '':
            self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))

        second_colon = node.second_colon
        if isinstance(second_colon, Colon):
            if second_colon.whitespace_before.value != '':
                self.add_error('extra-leading-colon-whitespace', node=node, args=(':',))
            if second_colon.whitespace_after.value != '':
                self.add_error('extra-trailing-colon-whitespace', node=node, args=(':',))
