lambda a: a

lambda a, b, c: a, b, c

lambda a=1, b=2, c=3: a, b, c

lambda a, b, c=1: a, b, c

lambda a, b, c, d: a, b, c, d  # too-many-lambda-parameters

lambda a=1, b=2, c=3, d=4: a, b, c, d  # too-many-lambda-parameters

lambda a, b, c=1, d=2: a, b, c, d  # too-many-lambda-parameters
