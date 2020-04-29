lambda: True

lambda a: True

lambda a, /, b: True

lambda *args, b: True

lambda a, *args, **kwargs: True

lambda a=1, b=2, c=3: True

lambda a, b, c=1: True

lambda a, b, c, d: True  # too-many-lambda-parameters

lambda a=1, b=2, c=3, d=4: True  # too-many-lambda-parameters

lambda a, b, c=1, d=2: True  # too-many-lambda-parameters

lambda a, b, c, *args, **kwargs: True  # too-many-lambda-parameters

lambda *args, b, c, d: True  # too-many-lambda-parameters

lambda a, b, /, c=1, **kwargs: True  # too-many-lambda-parameters
