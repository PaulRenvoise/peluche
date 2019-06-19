import logging


class Progress():
    STYLES = ('quiet', 'dot', 'filename', 'percent', 'count')

    def __init__(self, style='dot'):
        self.logger = logging.getLogger(f"{__name__}.{style}")

        self.print_progress = getattr(self, f"_{style}")

    def initialize(self):
        pass

    def monitor(self, items):
        length = len(items)

        for index, item in enumerate(items, start=1):
            yield item

            self.print_progress(item, index, length)

    def finalize(self):
        pass

    def __enter__(self):
        self.initialize()

        return self

    def __exit__(self, type, value, traceback):
        self.finalize()

    def _quiet(self, _item, _index, _length):
        pass

    def _dot(self, _item, index, _length):
        self.logger.info('.' * index)

    def _filename(self, item, _index, _length):
        self.logger.info(item)

    def _percent(self, _item, index, length):
        percent = index * 100 / length

        self.logger.info("%i%%", percent)

    def _count(self, _item, index, length):
        self.logger.info("%i/%i", index, length)
