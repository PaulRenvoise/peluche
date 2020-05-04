def func():
    pass

def func():
    for i in x:
        if i % 2:
            try:
                yield i
            except Exception:
                pass

def func():
    for i in x:
        for j in y:
            if i % 2 and j % 2:
                if True:  # block-too-nested
                    try:
                        yield i, j
                    except Exception:
                        pass

def func():
    def inner_func():
        for i in x:
            for j in y:
                if i % 2 and j % 2:  # block-too-nested
                    if True:
                        try:
                            yield i, j
                        except Exception:
                            pass

def func():
    if True:
        pass
    elif True:
        pass
    elif True:
        pass
    elif True:
        pass
    elif True:
        pass
    else:
        pass

def func():
    if var == 1:
        pass
    elif var == 2:
        pass
    elif var == 3:
        if should_iterate:
            for i in range(2):
                if i % 2:  # block-too-nested
                    print(i)
