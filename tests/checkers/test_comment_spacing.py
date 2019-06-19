# Classes

class Cls():  # OK
    pass
class Cls():#KO
    pass
class Cls():  #KO
    pass
class Cls():# KO
    pass
class Cls():   # KO
    pass

# Functions, methods, lambdas

def func():  # OK
    pass
def func():#KO
    pass
def func():  #KO
    pass
def func():# KO
    pass
def func():   # KO
    pass

# Default

var = 1  # OK
var = 2#KO
var = 3  #KO
var = 4# KO
var = 5   # KO

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

# OK
class Cls():
    # OK
    def __init__(self):
        # OK
        pass

comment.string[1:].strip()  # regression: #embedded comment

from module import (  # FIXME: shouldn't fail
    cls,
    other_clas,
)

if cond and (  # FIXME: shouldn't fail
        nested_cond or other_nested_cond
        ):
    pass

func(arg1,
     arg2, # FIXME: should fail
     arg3)

return  # FIXME: shouldn't fail

lst = [
    1,  # FIXME: shouldn't fail
    2,
    3,
]
