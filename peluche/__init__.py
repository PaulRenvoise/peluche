import logging
import logging.config


DEFAULT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'incremental': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        },
        'no_info': {
            'format': '%(message)s'
        },
        'no_info_no_newline': {
            'format': '\x1b[1A%(message)s'
        },
        'no_info_replace': {
            'format': '\x1b[80D\x1b[1A\x1b[K%(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
            'level': 'DEBUG',
        },
        'dot': {
            'class': 'logging.StreamHandler',
            'formatter': 'no_info_no_newline',
            'level': 'INFO',
        },
        'filename': {
            'class': 'logging.StreamHandler',
            'formatter': 'no_info',
            'level': 'INFO',
        },
        'percent': {
            'class': 'logging.StreamHandler',
            'formatter': 'no_info_replace',
            'level': 'INFO',
        },
    },
    'loggers': {
        'peluche.progress.dot': {
            'handlers': ['dot'],
            'level': 'INFO',
            'propagate': False,
        },
        'peluche.progress.filename': {
            'handlers': ['filename'],
            'level': 'INFO',
            'propagate': False,
        },
        'peluche.progress.percent': {
            'handlers': ['percent'],
            'level': 'INFO',
            'propagate': False,
        },
        'peluche.progress.count': {
            'handlers': ['percent'],
            'level': 'INFO',
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    }
}
logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)

try:
    from flashback.debugging import xp
except ImportError:
    def xp(*args, **kwargs):
        pass
finally:
    __builtins__['xp'] = xp

from .monkey import *

from .__pkg__ import __version__
from .peluche import Peluche


__all__ = (
    'Peluche',
)
