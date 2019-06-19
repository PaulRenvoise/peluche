from blinker import signal

from ..message import Message


class BaseChecker():
    NAME = None
    DESCRIPTION = None
    OPTIONS = {}
    MESSAGES = {}
    IS_ENABLED = True

    def __init__(self):
        self.OPTIONS.update({
            'enabled': {
                'default': True,
                'type': 'bool',
                'metavar': '<True or False>',
                'help': """
                Whether or not to use the checker.
                """,
            },
        })

    def add_error(self, error_id, args=None, node=None):
        content = self.MESSAGES[error_id]['template'].format(*args)

        print(Message(error_id, content, node=node))

        return True

    @property
    def name(self):
        return self.NAME
