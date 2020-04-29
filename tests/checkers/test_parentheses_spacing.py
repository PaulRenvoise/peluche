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
def func(a):
    pass
def func( a ):  # KO
    pass
def func(a ):  # KO
    pass
def func( a):  # KO
    pass
def func(
        a,
        b,
        c,
):
    pass
def func(
        a,
        b,
        c,
        ):
    pass
def func( 
        a,
        b,
        c,
        ):
    pass
def func(
        a,
        b,
        c,
 ):
    pass

# Calls

func()
func( )  # KO
func ()  # KO
func(a)
func( a )  # KO
func(a )  # KO
func( a)  # KO
func(
    a
    )
func(
    a
)
func( 
    a
)
func(
 a
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
    'statement'
)
(
    'statement'
 )
