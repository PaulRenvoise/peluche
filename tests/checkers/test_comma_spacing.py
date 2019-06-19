# Functions, methods, lambdas

def func(a, b, c, d, e=1):  # OK
    pass
def func(a,b , c ,d,  e=1):  # KO
    pass

lambda a, b, c, d, e=1: True  # OK
lambda a,b , c ,d,  e=1: True  # KO

# Calls

func(a, b, c, d, e=1)  # OK
func(a,b , c ,d,  e=1)  # KO

# Iterables

('tuple',)  # OK
['list',]  # KO
{'set',}  # KO
{'dict': 1,}  # KO

('tuple', 'tuple', 'tuple', 'tuple', 'tuple')  # OK
('tuple','tuple' , 'tuple' ,'tuple',  'tuple')  # KO
['list', 'list', 'list', 'list', 'list']  # OK
['list','list' , 'list' ,'list',  'list']  # KO
{'set', 'set', 'set', 'set', 'set'}  # OK
{'set','set' , 'set' ,'set',  'set'}  # KO
{'dict': 1, 'dict': 1, 'dict': 1, 'dict': 1, 'dict': 1}  # OK
{'dict': 1,'dict': 1 , 'dict': 1 ,'dict': 1,  'dict': 1}  # KO
