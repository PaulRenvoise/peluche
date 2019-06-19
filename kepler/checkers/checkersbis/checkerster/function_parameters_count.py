from .base import BaseChecker


class FunctionParametersCount(BaseChecker):
    NAME = 'function_parameters_count'
    DESCRIPTION = 'Checks the maximum number of parameters allowed.'
    OPTIONS = {
        'max': {
            'default': 5,
            'type': 'int',
            'metavar': 'COUNT',
            'help': """
                The maximum number of parameters allowed.
            """,
        },
        'ignore-kwargs': {
            'default': False,
            'type': 'bool',
            'metavar': 'TRUE or FALSE',
            'help': """
                Whether or not to ignore keyword arguments.
            """
        }
    }
    MESSAGES = {
        'too-many-function-parameters': {
            'template': "Too many function parameters ({!r}/{!r}).",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_def(self, node):
        # ap(node.fst())

        parameters = node.find_all('def_argument')
        if False:
            parameters = [parameter for parameter in parameters if parameter.value is None]

        count = len(parameters)

        if count > 5:
            self.add_error('too-many-function-parameters', node=node, args=(count, 5))
