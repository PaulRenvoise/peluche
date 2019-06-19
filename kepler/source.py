import baron
from redbaron import RedBaron


class Source:
    def __init__(self, filename):
        self.filename = filename

        self.raw = open(filename, 'r').read()

        self.ast, self.fst = self._parse(self.raw)

        # Sets the deactivated checkers per line
        self.lines_count = len(self.raw.splitlines())
        self.lines = [set() for _ in range(self.lines_count)]

        for comment in self.ast.find_all('comment'):
            if comment.value.startswith('# kepler:disable '):
                self._disable_checkers_with_comment(comment)
            elif comment.value.startswith('# kepler:enable '):
                self._enable_checkers_with_comment(comment)
            else:
                continue

    def _parse(self, raw):
        try:
            ast = RedBaron(raw)
        except baron.parser.ParsingError as error:
            # TODO: log something? What's the wanted behavior here?
            raise error

        return [ast, ast.fst()]

    def _disable_checkers_with_comment(comment):
        checkers = set(comment.value[17:].split(', '))
        position = comment.absolute_bounding_box.top_left

        if len(comment.formatting) == 0:
            for index in range(position.line, self.lines_count):
                self.lines[index - 1] |= checkers
        else:
            self.lines[position.line - 1] |= checkers

    def _enable_checkers_with_comment(comment):
        checkers = set(comment.value[16:].split(', '))
        position = comment.absolute_bounding_box.top_left

        if len(comment.formatting) == 0:
            for index in range(position.line, self.lines_count):
                self.lines[index - 1] -= checkers
        else:
            self.lines[position.line - 1] -= checkers

    def __repr__(self):
        return self.filename

    def __str__(self):
        return self.filename
