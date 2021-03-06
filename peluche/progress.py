import logging


class Progress:
    """
    TODO
    """
    STYLES = ('quiet', 'dot', 'filename', 'percent', 'count')

    def __init__(self, style='dot'):
        """
        TODO
        """
        self.logger = logging.getLogger(f"{__name__}.{style}")

        self.print_progress = getattr(self, f"_{style}")

    def initialize(self):
        """
        TODO
        """
        pass

    def monitor(self, items):
        """
        TODO
        """
        length = len(items)

        for index, item in enumerate(items, start=1):
            yield item

            self.print_progress(item, index, length)

    def finalize(self):
        """
        TODO
        """
        pass

    def _quiet(self, _item, _index, _length):
        pass

    def _dot(self, _item, index, length):
        self.logger.info('.')

        # Since the logger does not print trailing newlines
        # We need to add one at the end
        if index == length:
            self.logger.info("\n")

    def _filename(self, item, _index, _length):
        self.logger.info(item)

    def _percent(self, _item, index, length):
        percent = index * 100 / length

        self.logger.info("%i%%", percent)
        if index == length:
            self.logger.info("\n")

    def _count(self, _item, index, length):
        self.logger.info("%i/%i", index, length)

        if index == length:
            self.logger.info("\n")
