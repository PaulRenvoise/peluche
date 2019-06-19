# Assignments

var = 1  # OK
var=1  # KO
var =1  # KO
var= 1  # KO
var  = 1  # KO
var =  1  # KO
func(a=1)  # OK, not an assignment

var += 1  # OK
var+=1  # KO
var -=1  # KO
var  *= 1  # KO
var /=  1  # KO

# Comparisons

1 > 2  # OK
1 < 2 <= 3  # OK
1 in [1, 2]  # OK
1<2  # KO
1<2<3  # KO
'a'in'aaa'  # KO
1 >= 2 >=3  # KO
'a'  in 'aaa'  # KO
1  != 2 < 3  # KO
1 < 2 <>  3  # KO
'a'in 'aaa'  # KO

# Binary Operations

1 + 2  # OK
1 ** 2  # OK
1/2  # KO
1 -2  # KO
1- 2  # KO
1 +  2  # KO
1  % 2  # KO

# Boolean Operations

'a' or 'b'  # OK
'a'and'b'  # KO
'a'or 'b'  # KO
'a' and'b'  # KO
'a' or  'b'  # KO
'a'  and 'b'  # KO

# Unitary Operations

-1  # OK
- 1  # KO
1 * +1  # OK
1 -+1  # KO
1 /+ 1  # KO
not 1  # OK
not'1'  # KO
