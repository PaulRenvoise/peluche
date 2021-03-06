from libcst import Param

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
        },
        'ignore-stars': {
            'default': False,
            'type': 'bool',
            'metavar': 'TRUE or FALSE',
            'help': """
                Whether or not to ignore starred arguments.
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

    def visit_FunctionDef(self, node):
        parameters = node.params.params
        parameters += node.params.posonly_params

        if False:  # ignore-kwargs=False
            parameters = [parameter for parameter in parameters if parameter.default is None]
        else:
            parameters += node.params.kwonly_params

        if not False:  # ignore-stars=False
            star_arg = node.params.star_arg
            if isinstance(star_arg, Param):
                parameters += (star_arg,)

            star_kwarg = node.params.star_kwarg
            if isinstance(star_kwarg, Param):
                parameters += (star_kwarg,)

        count = len(parameters)

        if count > 5:
            self.add_error('too-many-function-parameters', node=node, args=(count, 5))
