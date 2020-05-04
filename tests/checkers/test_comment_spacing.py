# Classes

class Cls():  # OK
    pass
class Cls(): # KO
    pass
class Cls():   # KO
    pass

# Functions, methods, lambdas

def func():  # OK
    pass
def func(): # KO
    pass
def func():   # KO
    pass

# Default

var = 1  # OK
var = 2 # KO
var = 3   # KO

# Try/excepts

try:  # OK
    pass
except:  # OK
    pass
try:# KO
    pass
except:# KO
    pass
try:   # KO
    pass
except:   # KO
    pass

# Inline comments

comment.string[1:].strip()  # OK for an # embedded comment

from module import (  # OK
    cls,
    other_clas,
)

if cond and (  # OK
        nested_cond or other_nested_cond
        ):
    pass

func(arg1,
     arg2, # KO
     arg3)

return  # OK

lst = [
    1,  # OK
    2,
    3,
]

# Not inline comments

  # KO
# OK
class Cls():
        # KO
  # KO
# KO
    # OK
    def __init__(self):
                # KO
    # KO
# KO
        # OK
        if True:
                 # KO
        # KO
# KO
            # OK
            return True

lst = [
    # OK
    [
        1,
        2,
        3
    ],
# KO
    [
        'a',
        'b',
        'c'
    ],
  # KO
    [
        1.0,
        2.0,
        3.0
    ]
        # KO
    [
        '!',
        '@',
        '#'
    ]
]

def func(a, b):
    c = 0

        # KO
  # KO
# KO
    # OK
    for j in range(i):
            # KO
    # KO
# KO
        # OK
        if i == j:
            if i != 0:
                c += a

            # Ok for block above
    # KO
# KO
        # OK
        if i != j:
            if i != 0:
                c += a

    # OK
    return c
