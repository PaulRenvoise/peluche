# Classes

class Cls():
    pass

class Cls( ):  # KO
    pass

class Cls ():  # KO
    pass

class Cls(object):
    pass

class Cls( object ):  # KO
    pass

class Cls(object ):  # KO
    pass

class Cls( object):  # KO
    pass

class Cls(
    object
):
    pass

class Cls(
    object  # comment
):
    pass

class Cls(
    object
    ):
    pass

class Cls (
    object
):
    pass

class Cls( 
    object
):
    pass

class Cls(
    object
 ):
    pass

# Defs

def func():
    pass

def func( ):  # KO
    pass

def func ():  # KO
    pass

def func(a, b):
    pass

def func( a, b ):  # KO
    pass

def func(a, b ):  # KO
    pass

def func( a, b):  # KO
    pass

def func(
        a,
        b
):
    pass

def func(
        a,
        b  # comment
):
    pass

def func(
        a,
        b
        ):
    pass

def func (
        a,
        b
):
    pass

def func( 
        a,
        b
):
    pass

def func(
        a,
        b
 ):
    pass

# Calls

func()
func( )  # KO
func ()  # KO
func(a, b)
func( a, b )  # KO
func(a, b )  # KO
func( a, b)  # KO
func(
    a,
    b
)
func(
    a,
    b  # comment
)
func (
    a,
    b
)
func( 
    a,
    b
)
func(
    a,
    b
 )

# Tuples

()
( )  # KO
('tuple',)
( 'tuple', )  # KO
( 'tuple',)  # KO
('tuple', )  # KO
('tuple', )  # KO
('tuple', 'tuple', )  # KO

# Excepts

try:
    pass
except:
    pass
except (RuntimeError):
    pass
except(RuntimeError):  # KO
    pass

# Prints

print('print')
print ('print')  # KO

# AssociativeParentheses

('statement')
(1 + 1) * 2  # KO
( 'state' + 'ment' )  # KO
( 's' * 2)  # KO
(2 / 1 )  # KO
(
    'statement'
)
(
    'statement'  # comment
)
( 
    'statement'
)
(
    'statement'
 )
(
    'statement'
) 
