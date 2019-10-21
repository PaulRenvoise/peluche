import os
import hashlib

import baron
from redbaron import RedBaron


class Source:
    """
    TODO
    """
    def __init__(self, filepath):
        """
        TODO
        """
        self.filepath = filepath
        self.filename = os.path.split(filepath)[1]
        self.extension = os.path.splitext(self.filename)[1]

        self.raw = open(filepath, 'r').read()
        self.lines = self.raw.splitlines()

        self.sha1 = hashlib.sha1(self.raw.encode('utf-8')).hexdigest()

        # Sets the deactivated checkers per line
        # self.lines_count = len(self.lines)
        # self.lines = [set() for _ in range(self.lines_count)]

        # for comment in self.ast.find_all('comment'):
        #     if comment.value.startswith('# kepler:disable '):
        #         self._disable_checkers_with_comment(comment)
        #     elif comment.value.startswith('# kepler:enable '):
        #         self._enable_checkers_with_comment(comment)
        #     else:
        #         continue

    @property
    def ast(self):
        try:
            return self._ast
        except AttributeError:
            self._ast = self._parse(self.raw)

            return self._ast

    @property
    def fst(self):
        try:
            return self._fst
        except AttributeError:
            # Calls `.ast()` that will call `._parse()` if `_ast` is not set
            self._fst = self.ast.fst()

            return self._fst

    def _parse(self, raw):
        try:
            ast = RedBaron(raw)
        except baron.parser.ParsingError as error:
            # TODO: log something? What's the wanted behavior here?
            raise error

        return ast

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
        return self.filepath

    def __str__(self):
        return self.filepath
