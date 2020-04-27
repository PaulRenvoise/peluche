from .base import BaseChecker


class EnumerationRefactoring(BaseChecker):
    NAME = 'enumeration_refactoring'
    DESCRIPTION = 'Checks for refactoring of non-optimized enumerations.'
    OPTIONS = {}
    MESSAGES = {
        'faster-enumeration': {
            'template': "Replace call to `{!r}` by `enumerate({!r})` as it is .9x faster.",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_for(self, node):
        # Checks for `for i in var`
        if node.target.type != 'atomtrailers':
            return
        if len(node.target.value) > 2:
            return

        # Checks for `for i in method()`
        range_node = node.target.find('name', value='range')
        if range_node is None:
            return
        range_call_node = node.target.find('call')
        if range_call_node is None or not range_call_node.is_neighbor(range_node):
            return
        # There's a step parameter in `range()`
        if len(range_call_node.value) > 2:
            return
        # Call to `range(x, y[, z])` starting at something else than 0
        if len(range_call_node.value) == 2 and range_call_node.value[0].value.value != '0':
            return

        # Checks for `for i in range(method())`
        len_node = range_call_node.value.find('name', value='len')
        if len_node is None:
            return
        len_call_node = range_call_node.value.find('call')
        if len_call_node is None or not len_call_node.is_neighbor(len_node):
            return

        # Checks for `for i in range(len([1, 2, 3, 4]))`
        name_node = len_call_node.value.find('name')
        if name_node is None:
            return

        # Now, we're sure to have `for i in range([0, ]len(iterable))`
        # Checks for `iterable[i]` or `iterable[:i:]` within the `for`
        getitem_node = node.value.find('getitem', value=node.iterator)
        if getitem_node is None:
            return
        atomtrailers_node = getitem_node.parent
        name_node_bis = atomtrailers_node.find('name', value=name_node.value)
        if name_node_bis is None or not getitem_node.is_neighbor(name_node_bis):
            return

        self.add_error('faster-enumeration', node=node.target, args=(node.target, name_node))
