import os
import hashlib

import libcst


class Source:
    """
    TODO
    """
    def __init__(self, filepath):
        """
        TODO
        """
        self.filepath = filepath
        self.relpath = os.path.relpath(filepath)
        self.filename = os.path.split(filepath)[1]
        self.basename, self.extension = os.path.splitext(self.filename)

        self.raw = open(filepath, 'r').read()
        self.lines = self.raw.splitlines()

        self.sha1 = hashlib.sha1(self.raw.encode('utf-8')).hexdigest()

        # Sets the deactivated checkers per line
        # self.lines_count = len(self.lines)
        # self.lines = [set() for _ in range(self.lines_count)]

        # for comment in self.cst.find_all('comment'):
        #     if comment.value.startswith('# peluche:disable '):
        #         self._disable_checkers_with_comment(comment)
        #     elif comment.value.startswith('# peluche:enable '):
        #         self._enable_checkers_with_comment(comment)
        #     else:
        #         continue

    @property
    def cst(self):
        try:
            return self._cst
        except AttributeError:
            self._cst = self._parse(self.raw)

            return self._cst

    def _parse(self, raw):
        try:
            cst = libcst.parse_module(raw)
            annotated_cst = libcst.MetadataWrapper(cst)
        except libcst._exceptions.ParserSyntaxError as error:
            # TODO: log something? What's the wanted behavior here?
            raise error

        return annotated_cst

    def _disable_checkers_with_comment(self, comment):
        checkers = set(comment.value[17:].split(', '))
        position = comment.absolute_bounding_box.top_left

        if len(comment.formatting) == 0:
            for index in range(position.line, self.lines_count):
                self.lines[index - 1] |= checkers
        else:
            self.lines[position.line - 1] |= checkers

    def _enable_checkers_with_comment(self, comment):
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
