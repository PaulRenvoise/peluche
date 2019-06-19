def func():
    pass

def func(a, b, c, d, e):
    pass

def func(a=1, b=2, c=3, d=4, e=5):
    pass

def func(a, b, c, d=1, e=2):
    pass

def func(a, b, c, d, e, f):  # too-many-function-parameters
    pass

def func(a=1, b=2, c=3, d=4, e=5, f=6):  # too-many-function-parameters
    pass

def func(a, b, c, d=1, e=2, f=3):  # too-many-function-parameters
    pass
