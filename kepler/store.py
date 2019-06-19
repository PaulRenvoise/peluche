from collections import defaultdict


class Store():
    def __init__(self):
        self.storage = defaultdict(list)

    def dump(self):
        for filename, values in self.storage.items():
            for message, markup in values:
                print(f"{filename}:{message}")
                print(markup)

    @property
    def is_empty(self):
        return not bool(self.storage)
