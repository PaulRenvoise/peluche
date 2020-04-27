from .base import BaseChecker

class MLBaseChecker(BaseChecker):
    def __init__(self):
        super().__init__()

        self.OPTIONS.update({
            'threshold': {
                'default': 0.7,
                'type': 'float',
                'metavar': '<Float>',
                'help': """
                The minimal confidence score required to trust the prediction.
                """,
            },
        })
