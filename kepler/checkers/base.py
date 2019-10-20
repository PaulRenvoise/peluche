from ..message import Message


class BaseChecker():
    NAME = None
    DESCRIPTION = None
    OPTIONS = {}
    MESSAGES = {}

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

    def add_error(self, error_id, args=None, node=None):
        content = self.MESSAGES[error_id]['template'].format(*args)

        print(Message(error_id, content, node=node))

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
