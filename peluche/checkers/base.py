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

        # FIXME: We should share the current file being processed
        # some way else (maybe with something like Rails' CurrentAttribute?)
        self.source = None

        self.errors = []

    @property
    def name(self):
        return self.NAME

    def prepare(self, source):
        self.errors = []
        self.source = source

    def add_error(self, error_id, args=None, node=None, position=None):
        """
        TODO
        """
        content = self.MESSAGES[error_id]['template'].format(*args)
        if node is not None:
            position = self.get_metadata(PositionProvider, node).start
        else:
            position = CodePosition(*position)

        message = Message(error_id, content, position=position)
        self.errors.append(message)

    def get_config(self):
        configuration = dict()

        configuration[self.NAME] = {}
        configuration[self.NAME]['description'] = self.DESCRIPTION

        for key, value in self.OPTIONS.items():
            if value['help'] != '':
                configuration[self.NAME][f"# {value['help'].strip()}"] = None

            configuration[self.NAME][key] = value['default']

        return configuration
