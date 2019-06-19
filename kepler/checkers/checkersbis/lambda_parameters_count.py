from .base import BaseChecker


class LambdaParametersCount(BaseChecker):
    NAME = 'lambda_parameters_count'
    DESCRIPTION = 'Checks the maximum number of parameters allowed.'
    OPTIONS = {
        'max': {
            'default': 3,
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
        'too-many-lambda-parameters': {
            'template': "Too many lambda parameters ({!r}/{!r}).",
            'description': """
            """,
        },
    }

    def __init__(self):
        super().__init__()

    def on_lambda(self, node):
        # ap(node.fst())

        parameters = node.find_all('def_argument')
        if False:
            parameters = [parameter for parameter in parameters if parameter.value is None]

        count = len(parameters)

        if count > 3:
            self.add_error('too-many-lambda-parameters', node=node, args=(count, 3))
