from collections import defaultdict


class Registry():
    def __init__(self):
        self._registry = defaultdict(list)

    def register(self, registree):
        self._registry[registree.name].append(registree)

    @property
    def all(self):
        return self._registry
