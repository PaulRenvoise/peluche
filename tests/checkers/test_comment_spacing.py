# Classes

class Cls():  # OK
    pass
class Cls(): # KO
    pass
class Cls():   # KO
    pass
class Cls():  #KO
    pass

# Functions, methods, lambdas

def func():  # OK
    pass
def func(): # KO
    pass
def func():   # KO
    pass
def func():  #KO
    pass

# Default

var = 1  # OK
var = 2 # KO
var = 3   # KO
var = 4  #KO

# Try/excepts

try:  # KO
    pass
except:  # KO
    pass
try:#KO
    pass
except:#KO
    pass
try:  #KO
    pass
except:  #KO
    pass
try:# KO
    pass
except:# KO
    pass
try:   # KO
    pass
except:   # KO
    pass

# Comments

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

# OK
  # KO
#KO
class Cls():
    # OK
        # KO
  # KO
# KO
    def __init__(self):
        # OK
# KO
                # KO
    # KO
        if True:
            # OK
                 # KO
        # KO
# KO
            return True
