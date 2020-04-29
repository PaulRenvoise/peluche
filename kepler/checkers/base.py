from libcst import CSTVisitor
from libcst.metadata import PositionProvider, ParentNodeProvider, ScopeProvider
from libcst.metadata import CodePosition


from ..message import Message


class BaseChecker(CSTVisitor):
    NAME = None
    DESCRIPTION = None
    OPTIONS = {}
    MESSAGES = {}

    METADATA_DEPENDENCIES = (
        PositionProvider,
        ParentNodeProvider,
        ScopeProvider,
    )

    def __init__(self):
        self.OPTIONS.update({
            'enabled': {
                'default': True,
                'type': 'bool',
                'metavar': '<Bool>',
                'help': """""",
            },
        })

    @property
    def name(self):
        return self.NAME

    def add_error(self, error_id, args=None, node=None, position=None):
        """
        TODO
        """
        content = self.MESSAGES[error_id]['template'].format(*args)
        if node is not None:
            position = self.get_metadata(PositionProvider, node).start
        else:
            position = CodePosition(*position)

        print(Message(error_id, content, position=position))

        return True

    def get_config(self):
        configuration = dict()

        configuration[self.NAME] = {}
        configuration[self.NAME]['description'] = self.DESCRIPTION

        for key, value in self.OPTIONS.items():
            if value['help'] != '':
                configuration[self.NAME][f"# {value['help'].strip()}"] = None

            configuration[self.NAME][key] = value['default']

        return configuration
