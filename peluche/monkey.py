from libcst._nodes.internal import CodegenState
from libcst import CSTNode
from libcst.metadata import CodeRange


def code(self):
    state = CodegenState(
        default_indent=' ' * 4,  # TODO: take in account the config
        default_newline="\n"  # TODO: take in account the config
    )
    self._codegen(state)

    return ''.join(state.tokens)


CSTNode.code = property(code)

def length(self):
    return self.end.line - self.start.line + 1

CodeRange.length = property(length)
