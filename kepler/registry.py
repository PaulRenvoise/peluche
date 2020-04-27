from collections import defaultdict


class Registry:
    """
    TODO
    """
    def __init__(self):
        """
        TODO
        """
        self._registry = defaultdict(list)

    def register(self, registree):
        """
        TODO
        """
        self._registry[registree.name].append(registree)

    @property
    def all(self):
        return self._registry
