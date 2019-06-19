import re

from .base import BaseChecker


class CommentSpacing(BaseChecker):
    NAME = 'comment_spacing'
    DESCRIPTION = 'Checks the compliance with spacing rules before comments.'
    OPTIONS = {}
    MESSAGES = {
        'missing-comment-whitespace': {
            'template': "Missing whitespace around {!r}.",
            'description': """
            """,
        },
        'leading-comment-whitespace': {
            'template': "Extraneous leading whitespace before {!r}.",
            'description': """
            """,
        },
        'trailing-comment-whitespace': {
            'template': "Extraneous trailing whitespace after {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_class(self, node):
        # ap(node.fst())

        comment_node = node.sixth_formatting.comment
        if comment_node is None:
            return

        supposed_space_node = node.sixth_formatting[0]
        if supposed_space_node == comment_node:
            self.add_error('missing-comment-whitespace', node=comment_node, args=('#',))
        elif supposed_space_node.value.startswith('   '):
            self.add_error('leading-comment-whitespace', node=supposed_space_node, args=('#',))
        elif supposed_space_node.value != '  ':
            self.add_error('missing-comment-whitespace', node=supposed_space_node, args=('#',))
        elif re.match(r"#[^\s]", comment_node.value):
            self.add_error('missing-comment-whitespace', node=comment_node, args=('#',))

    def on_def(self, node):
        # ap(node.fst())

        comment_node = node.sixth_formatting.comment
        if comment_node is None:
            return

        supposed_space_node = node.sixth_formatting[0]
        if supposed_space_node == comment_node:
            self.add_error('missing-comment-whitespace', node=comment_node, args=('#',))
        elif supposed_space_node.value.startswith('   '):
            self.add_error('leading-comment-whitespace', node=supposed_space_node, args=('#',))
        elif supposed_space_node.value != '  ':
            self.add_error('missing-comment-whitespace', node=supposed_space_node, args=('#',))
        elif re.match(r"#[^\s]", comment_node.value):
            self.add_error('missing-comment-whitespace', node=comment_node, args=('#',))

    def on_try(self, node):
        # ap(node.fst())

        comment_node = node.second_formatting.comment
        if comment_node is None:
            return

        supposed_space_node = node.second_formatting[0]
        if supposed_space_node == comment_node:
            self.add_error('missing-comment-whitespace', node=comment_node, args=('#',))
        elif supposed_space_node.value.startswith('   '):
            self.add_error('leading-comment-whitespace', node=supposed_space_node, args=('#',))
        elif supposed_space_node.value != '  ':
            self.add_error('missing-comment-whitespace', node=supposed_space_node, args=('#',))
        elif re.match(r"#[^\s]", comment_node.value):
            self.add_error('missing-comment-whitespace', node=comment_node, args=('#',))

    def on_except(self, node):
        # ap(node.fst())

        comment_node = node.fifth_formatting.comment
        if comment_node is None:
            return

        supposed_space_node = node.fifth_formatting[0]
        if supposed_space_node == comment_node:
            self.add_error('missing-comment-whitespace', node=comment_node, args=('#',))
        elif supposed_space_node.value.startswith('   '):
            self.add_error('leading-comment-whitespace', node=supposed_space_node, args=('#',))
        elif supposed_space_node.value != '  ':
            self.add_error('missing-comment-whitespace', node=supposed_space_node, args=('#',))
        elif re.match(r"#[^\s]", comment_node.value):
            self.add_error('missing-comment-whitespace', node=comment_node, args=('#',))

    def on_comment(self, node):
        # ap(node.parent.fst())

        root = node.root
        if root.at(node.absolute_bounding_box.top_left.line) == node:
            return

        space_node = node.formatting.space

        if space_node is not None:
            if space_node.value.startswith('   '):
                self.add_error('leading-comment-whitespace', node=space_node, args=('#',))
            elif space_node.value != '  ':
                self.add_error('missing-comment-whitespace', node=space_node, args=('#',))
            elif re.match(r"#[^\s]", node.value):
                self.add_error('missing-comment-whitespace', node=node, args=('#',))
        else:
            self.add_error('missing-comment-whitespace', node=node, args=('#',))
