def func():
    """
    Docstring
    """
    pass

def func():  # missing-function-docstring
    pass

def func():  # missing-function-docstring
    """
    """
    pass

def func():
    """
    Docstring
    """
    def nested_function():
        pass

def _private_func():
    pass
