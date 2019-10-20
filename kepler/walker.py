import logging


class Walker:
    """
    TODO
    """
    def __init__(self, source, checkers, config):
        """
        TODO
        """
        self.source = source
        self.checkers = checkers
        self.config = config

        self.exceptions = {}

        self._callback2checker_callbacks = {}

    def walk(self):
        """
        TODO
        """
        # We need this first call to _visit_node() to emulate a "module" node.
        self._visit_node(self.source.ast)

        for node in self.source.ast:
            self._walk(node)

    def _walk(self, node):
        self._visit_node(node)

        for child in node.children:
            self._walk(child)

    def _visit_node(self, node):
        try:
            callback = f"on_{node.type}"
        except AttributeError:
            callback = 'on_module'

        try:
            for checker_callback in self._callback2checker_callbacks[callback]:
                try:
                    checker_callback(node)
                except Exception as e:
                    ap(node.absolute_bounding_box)
                    # ap(node.fst())
                    ap(checker_callback)
                    logging.exception(e)
        except KeyError:
            checker_callbacks = [getattr(checker, callback) for checker in self.checkers if hasattr(checker, callback)]
            self._callback2checker_callbacks[callback] = checker_callbacks

            self._visit_node(node)
