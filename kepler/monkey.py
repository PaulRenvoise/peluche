from redbaron import GenericNodesUtils
from redbaron import Node


def is_neighbor(self, rhs):
    if hasattr(self, 'index_on_parent') and hasattr(rhs, 'index_on_parent'):
        return self.index_on_parent == rhs.index_on_parent + 1

    return False


def scope(self):
    scope = self.parent_find(['class', 'def', 'lambda', 'generator_comprehension'])
    if scope is None:
        scope = self.root

    return scope


def absolute_top_line(self):
    return self.absolute_bounding_box.top_left.line


def absolute_bottom_line(self):
    return self.absolute_bounding_box.bottom_right.line


def absolute_left_column(self):
    return self.absolute_bounding_box.top_left.column


def absolute_right_column(self):
    return self.absolute_bounding_box.bottom_right.column


def absolute_length(self):
    return self.absolute_bottom_line - self.absolute_top_line + 1

def children(self):
    for kind, key, display in self._render():
        if kind in {'key', 'list'}:
            attr = getattr(self, key)

            if attr is None:
                continue

            if kind == 'key':
                yield attr
            elif kind == 'list':
                if hasattr(attr, 'node_list'):
                    attr = attr.node_list
                yield from attr

GenericNodesUtils.is_neighbor = is_neighbor
GenericNodesUtils.scope = property(scope)
GenericNodesUtils.absolute_top_line = property(absolute_top_line)
GenericNodesUtils.absolute_bottom_line = property(absolute_bottom_line)
GenericNodesUtils.absolute_left_column = property(absolute_left_column)
GenericNodesUtils.absolute_right_column = property(absolute_right_column)
GenericNodesUtils.absolute_length = property(absolute_length)
GenericNodesUtils.children = property(children)
