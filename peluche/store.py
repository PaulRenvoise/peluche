from collections import defaultdict


class Store:
    """
    TODO
    """
    def __init__(self):
        """
        TODO
        """
        self.storage = defaultdict(list)

    def dump(self):
        """
        TODO
        """
        for filename, values in self.storage.items():
            for message, markup in values:
                print(f"{filename}:{message}")
                print(markup)

    @property
    def is_empty(self):
        return not bool(self.storage)
