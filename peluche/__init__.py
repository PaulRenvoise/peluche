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
    },
    'handlers': {
        'console': {
            '()': 'flashback.logging.AffixedStreamHandler',
            'formatter': 'no_info',
            'level': 'DEBUG',
        },
        'dot': {
            '()': 'flashback.logging.AffixedStreamHandler',
            'formatter': 'no_info',
            'suffix': '',
            'level': 'INFO',
        },
        'filename': {
            '()': 'flashback.logging.AffixedStreamHandler',
            'formatter': 'no_info',
            'level': 'INFO',
        },
        'percent_or_count': {
            '()': 'flashback.logging.AffixedStreamHandler',
            'formatter': 'no_info',
            'prefix': '\x1b[80D\x1b[K',
            'suffix': '',
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
            'handlers': ['percent_or_count'],
            'level': 'INFO',
            'propagate': False,
        },
        'peluche.progress.count': {
            'handlers': ['percent_or_count'],
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
