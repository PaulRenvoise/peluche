from .base import BaseChecker


class ColonSpacing(BaseChecker):
    NAME = 'comma_spacing'
    DESCRIPTION = 'Checks the compliance with spacing rules around colons.'
    OPTIONS = {}
    MESSAGES = {
        'missing-colon-whitespace': {
            'template': "Missing whitespace after {!r}.",
            'description': """
            """,
        },
        'leading-colon-whitespace': {
            'template': "Extraneous leading whitespace before {!r}.",
            'description': """
            """,
        },
        'trailing-colon-whitespace': {
            'template': "Extraneous trailing whitespace after {!r}.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_class(self, node):
        if len(node.fifth_formatting) > 0:
            self.add_error('leading-colon-whitespace', node=node, args=(':',))

        try:
            value_node = node.value.node_list[0]

            if value_node.type == 'endl':
                if len(value_node.formatting) > 0:
                    self.add_error('trailing-colon-whitespace', node=value_node, args=(':',))
            else:  # We have a one-liner
                if node.sixth_formatting.value.startswith('  '):
                    self.add_error('trailing-colon-whitespace', node=node, args=(':',))
                elif node.sixth_formatting.value != ' ':
                    self.add_error('missing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            pass

    def on_def(self, node):
        if len(node.fifth_formatting) > 0:
            self.add_error('leading-colon-whitespace', node=node, args=(':',))

        # TODO: What if it's a one-liner?
        try:
            node = node.value.node_list[0]

            if node.type == 'endl':
                if len(node.formatting) > 0:
                    self.add_error('trailing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            pass

    def on_lambda(self, node):
        if len(node.second_formatting) > 0:
            self.add_error('leading-colon-whitespace', node=node, args=(':',))

        try:
            formatting = node.third_formatting[0]

            if formatting.value.startswith('  '):
                self.add_error('trailing-colon-whitespace', node=node, args=(':',))
            elif formatting.value != ' ':
                self.add_error('missing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            self.add_error('missing-colon-whitespace', node=node, args=(':',))

    def on_if(self, node):
        if len(node.second_formatting) > 0:
            self.add_error('leading-colon-whitespace', node=node, args=(':',))

        # TODO: What if it's a one-liner?
        try:
            node = node.value.node_list[0]

            if node.type == 'endl':
                if len(node.formatting) > 0:
                    self.add_error('trailing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            pass

    def on_elif(self, node):
        if len(node.second_formatting) > 0:
            self.add_error('leading-colon-whitespace', node=node, args=(':',))

        # TODO: What if it's a one-liner?
        try:
            node = node.value.node_list[0]

            if node.type == 'endl':
                if len(node.formatting) > 0:
                    self.add_error('trailing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            pass

    def on_else(self, node):
        if len(node.first_formatting) > 0:
            self.add_error('leading-colon-whitespace', node=node, args=(':',))

        # TODO: What if it's a one-liner?
        try:
            node = node.value.node_list[0]

            if node.type == 'endl':
                if len(node.formatting) > 0:
                    self.add_error('trailing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            pass

    def on_with(self, node):
        if len(node.second_formatting) > 0:
            self.add_error('leading-colon-whitespace', node=node, args=(':',))

        # TODO: What if it's a one-liner?
        try:
            node = node.value.node_list[0]

            if node.type == 'endl':
                if len(node.formatting) > 0:
                    self.add_error('trailing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            pass

    def on_try(self, node):
        if len(node.first_formatting) > 0:
            self.add_error('leading-colon-whitespace', node=node, args=(':',))

        # TODO: What if it's a one-liner?
        try:
            node = node.value.node_list[0]

            if node.type == 'endl':
                if len(node.formatting) > 0:
                    self.add_error('trailing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            pass

    def on_except(self, node):
        if node.exception is None:
            if len(node.first_formatting) > 0:
                self.add_error('leading-colon-whitespace', node=node, args=(':',))
        else:
            if len(node.fourth_formatting) > 0:
                self.add_error('leading-colon-whitespace', node=node, args=(':',))

        # TODO: What if it's a one-liner?
        try:
            node = node.value.node_list[0]

            if node.type == 'endl':
                if len(node.formatting) > 0:
                    self.add_error('trailing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            pass

    def on_finally(self, node):
        if len(node.first_formatting) > 0:
            self.add_error('leading-colon-whitespace', node=node, args=(':',))

        # TODO: What if it's a one-liner?
        try:
            node = node.value.node_list[0]

            if node.type == 'endl':
                if len(node.formatting) > 0:
                    self.add_error('trailing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            pass

    def on_for(self, node):
        if len(node.fourth_formatting) > 0:
            self.add_error('leading-colon-whitespace', node=node, args=(':',))

        # TODO: What if it's a one-liner?
        try:
            node = node.value.node_list[0]

            if node.type == 'endl':
                if len(node.formatting) > 0:
                    self.add_error('trailing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            pass

    def on_while(self, node):
        if len(node.second_formatting) > 0:
            self.add_error('leading-colon-whitespace', node=node, args=(':',))

        # TODO: What if it's a one-liner?
        try:
            node = node.value.node_list[0]

            if node.type == 'endl':
                if len(node.formatting) > 0:
                    self.add_error('trailing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            pass

    def on_format(self, node):
        pass

    def on_dictitem(self, node):
        if len(node.first_formatting) > 0:
            self.add_error('leading-colon-whitespace', node=node, args=(':',))

        try:
            formatting = node.second_formatting[0]

            if formatting.value.startswith('  '):
                self.add_error('trailing-colon-whitespace', node=node, args=(':',))
            elif formatting.value != ' ':
                self.add_error('missing-colon-whitespace', node=node, args=(':',))
        except IndexError:
            self.add_error('missing-colon-whitespace', node=node, args=(':',))

    # TODO: finish this shit
    def on_slice(self, node):
        spaces = []
        for index, prefix in enumerate(['first', 'second', 'third', 'fourth']):
            node_formatting = getattr(node, f"{prefix}_formatting")
            if len(node_formatting) > 0:
                spaces.append(index)

        if len(spaces) != 4:
            for index in spaces:
                if index % 2:
                    self.add_error('trailing-colon-whitespace', node=node, args=(':',))
                else:
                    self.add_error('leading-colon-whitespace', node=node, args=(':',))
