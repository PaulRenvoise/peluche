def func():
    pass


def func():
    pass

def func():  # missing-newlines-before-function
    pass



def func():  # extraneous-newlines-before-function
    pass


class Cls():
    def __init__(self):
        pass

    def meth(self):
        pass
    def meth(self):  # missing-newlines-before-function
        pass


    def meth(self):  # extraneous-newlines-before-function
        pass
