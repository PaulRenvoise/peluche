import builtins

from libcst.matchers import findall, Decorator, Name
from libcst.metadata import ScopeProvider, ClassScope
import regex

from .base import BaseChecker


class ParameterNaming(BaseChecker):
    NAME = 'parameter_naming'
    DESCRIPTION = 'Checks the compliance of parameter names with the naming convention.'
    OPTIONS = {
        'style': {
            'default': 'pascal_case',
            'type': 'str',
            'metavar': 'NAME',
            'help': """
                The naming style to enforce.
            """,
        },
    }
    MESSAGES = {
        'invalid-parameter-name': {
            'template': "Parameter name {!r} not following {!r} convention.",
            'description': """
                Following a unique naming style across all the codebase helps readability.
            """,
        },
        'builtin-parameter-name': {
            'template': "Parameter name {!r} is already defined as a builtin.",
            'description': """
                Overriding builtins with a variable can lead to unintended side-effects.
            """,
        },
        'bad-parameter-name': {
            'template': "Parameter name {!r} {}.",
            'description': """
            """,
        },
    }

    CRE_FORMATS = {
        'snake_case': regex.compile(r"^[a-z\d_]+$"),
        'camel_case': regex.compile(r"^[a-z][a-zA-Z\d]+$"),
        'pascal_case': regex.compile(r"^[A-Z][a-zA-Z\d]+$"),
        'upper_case': regex.compile(r"^[A-Z\d_]+$"),
    }

    MATCHER_CLASSMETHOD = Decorator(
        decorator=Name('classmethod')
    )

    MATCHER_STATICMETHOD = Decorator(
        decorator=Name('staticmethod')
    )

    # TODO: handle this in a config file
    BAD_PARAMETER_NAMES = {
        'foo',
        'bar',
        'baz',
        'data',
        'var',
        'param',
    }

    def __init__(self):
        super().__init__()

    def visit_FunctionDef(self, node):
        scope = self.get_metadata(ScopeProvider, node)
        for index, param_node in enumerate(node.params.all_params):
            param_name = param_node.name.value

            # Check the first parameter of non static methods
            if index == 0 and isinstance(scope, ClassScope) and not findall(node, self.MATCHER_STATICMETHOD):
                if findall(node, self.MATCHER_CLASSMETHOD):
                    if param_name != 'cls':
                        self.add_error('bad-parameter-name', node=param_node, args=(param_name, "should be 'cls'"))
                elif param_name != 'self':
                    self.add_error('bad-parameter-name', node=param_node, args=(param_name, "should be 'self'"))
            elif getattr(builtins, param_name, None):
                self.add_error('builtin-parameter-name', node=param_node, args=(param_name,))
            elif not self.CRE_FORMATS['snake_case'].match(param_name):
                self.add_error('invalid-parameter-name', node=param_node, args=(param_name, 'snake_case'))
            elif param_name in self.BAD_PARAMETER_NAMES:
                self.add_error('bad-parameter-name', node=param_node, args=(param_name, 'is blacklisted'))
