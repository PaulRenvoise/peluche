# Assignments

var = 1
var =\
1
var = \
1
func(a=1)
var += 1

var=1  # KO
var =1  # KO
var= 1  # KO
var  = 1  # KO
var =  1  # KO
var =  \
1  # KO
var+=1  # KO
var -=1  # KO
var  *= 1  # KO
var /=  1  # KO

# Comparisons

1 > 2
1 < 2 <= 3
1 in {1, 2}
1<2  # KO
1<2<3  # KO
1 >= 2 >=3  # KO
1  != 2 < 3  # KO
'a'in'aaa'  # KO
'a'  in 'aaa'  # KO
'a'in 'aaa'  # KO
'a' not in 'bbb'
'a'  not in 'bbb'  # KO
'a' not  in 'bbb'  # KO
'a'not in'bbb'  # KO

# Binary Operations

1 + 2
1 ** 2
1/2  # KO
1 -2  # KO
1- 2  # KO
1 +  2  # KO
1  % 2  # KO

# Boolean Operations

'a' or 'b'
'a'and'b'  # KO
'a'or 'b'  # KO
'a' and'b'  # KO
'a' or  'b'  # KO
'a'  and 'b'  # KO
if ('a' or
        'b'):
    pass
if ('a'
        or 'b'):
    pass
if ('a' or 
        'b'):  # KO
    pass
if ('a' 
        or 'b'):  # KO
    pass

# Unary Operations

-1
- 1  # KO
1 * +1
1 -+1  # KO
1 /+ 1  # KO
not 1
not'1'  # KO
not  '1'  # KO
~1
~ 1  # KO
