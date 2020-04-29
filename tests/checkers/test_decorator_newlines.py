# Functions

@contextmanager
def func():
    yield 1


@contextmanager

def func():
    yield 1


@cached
@contextmanager
def func():
    yield 1



@cached

@contextmanager

def func():
    yield 1


# Classes

class Cls():
    @property
    def prop(self):
        return self.prop

    @property

    def attr(self):
        return self.attr

    @cached
    @property
    def slow_prop(self):
        return self._compute_slow_prop()

    @cached


    @property

    def slow_attr(self):
        return self._compute_slow_attr()
