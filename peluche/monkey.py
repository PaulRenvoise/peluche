from libcst._nodes.internal import CodegenState
from libcst import CSTNode, Parameters, Param
from libcst.metadata import CodeRange


def code(self):
    state = CodegenState(
        default_indent=' ' * 4,  # TODO: take in account the config
        default_newline="\n"  # TODO: take in account the config
    )
    self._codegen(state)

    return ''.join(state.tokens)


def length(self):
    return self.end.line - self.start.line + 1


def all_params(self):
    parameters = self.params
    parameters += self.posonly_params
    parameters += self.kwonly_params

    star_arg = self.star_arg
    if isinstance(star_arg, Param):
        parameters += (star_arg,)

    star_kwarg = self.star_kwarg
    if isinstance(star_kwarg, Param):
        parameters += (star_kwarg,)

    return parameters


CSTNode.code = property(code)
CodeRange.length = property(length)
Parameters.all_params = property(all_params)
