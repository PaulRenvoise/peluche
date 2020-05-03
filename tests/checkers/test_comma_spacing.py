# Classes

class Cls(Parent, Parent):
    pass

class Cls(Parent,Parent , Parent ,Parent,  Parent):
    pass

class Cls(Parent,):
    pass

# Functions

def func(a, b, e=1):
    pass

def func(a, b, e=1, *args):
    pass

def func(a, b, **kwargs):
    pass

def func(a,b , c ,d,  e=1):
    pass

def func(a,):
    pass

def func(*args,):
    pass

def func(**kwargs):
    pass

# Lambdas

lambda a, b, e=1: True
lambda a, b, *args: True
lambda a,b , c ,d,  e=1: True  # KO
lambda a,: True
lambda a, b, /, d, e=1, *args,**kwargs,: True
lambda *args,: True
lambda **kwargs,: True

# Calls

func(a, b, e=1)
func(a,b , c ,d,  e=1)  # KO
func(
    a,
    b ,
    c, 
    d,
    e=1
)
func(a,)

# Iterables

('tuple',)
['list',]  # KO
{'set',}  # KO
{'dict': 1,}  # KO

('tuple', 'tuple', 'tuple', 'tuple', 'tuple')
('tuple','tuple' , 'tuple' ,'tuple',  'tuple')  # KO
['list', 'list', 'list', 'list', 'list']
['list','list' , 'list' ,'list',  'list']  # KO
{'set', 'set', 'set', 'set', 'set'}
{'set','set' , 'set' ,'set',  'set'}  # KO
{'dict': 1, 'dict': 1, 'dict': 1, 'dict': 1, 'dict': 1}
{'dict': 1,'dict': 1 , 'dict': 1 ,'dict': 1,  'dict': 1}  # KO

# Misc

lst = (
    (r"([iay])nges$", r"\1nx", None),  # should not fail
    (r"ises$", "is", "is-ises")
)
