import os
import logging
import subprocess
import time

from collections import defaultdict
from configparser import ConfigParser

from flashback import timeable

from .__pkg__ import __version__
from .checkers import BaseChecker
from .checkers import *  # Registers the checkers as subclasses of BaseChecker
from .finder import Finder
from .progress import Progress
from .source import Source


class Peluche:
    """
    TODO
    """
    OPTIONS = {
        'formatter': {
            'default': 'dot',
            'type': 'str',
            'metavar': 'FORMATTER',
            'help': """
                The formatter to use to report the progress.
            """,
        },
        'strict': {
            'default': False,
            'type': 'bool',
            'metavar': '<Bool>',
            'help': """
                Whether or not to exit at the first error encountered.
            """,
        },
        'processes': {
            'default': -1,
            'type': 'int',
            'metavar': 'PROCESSES',
            'help': """
                The number of processes to use when analyzing.
            """,
        },
        'include': {
            'default': '.py,',
            'type': 'str',
            'metavar': 'EXTENSIONS/FOLDERS',
            'help': """
                The extensions/folders to take in account when searching files to analyze.
            """,
        },
        'exclude': {
            'default': '.git/,',
            'type': 'str',
            'metavar': 'EXTENSIONS/FOLDERS',
            'help': """
                The extensions/folders to ignore when searching files to analyze.
            """,
        },
    }
    def __init__(self, args, reporter=None, config=None):
        """
        TODO
        """
        self.args = args

    @property
    def version(self):
        print(__version__)

    @timeable
    def analyze(self):
        """
        TODO
        """
        checkers = [checker() for checker in BaseChecker.__subclasses__()]

        finder = Finder()

        errors = defaultdict(list)

        progress = Progress(style=self.args.formatter)
        progress.initialize()

        for filepath in progress.monitor(finder.find_files(self.args.paths)):
            source = Source(filepath)
            for checker in checkers:
                checker.prepare(source)

                source.cst.visit(checker)

                errors[source.relpath].extend(checker.errors)

        progress.finalize()

        for relpath, messages in errors.items():
            for message in messages:
                logging.info(f"{relpath}:{message}")

        errors_count = len([value for values in errors.values() for value in values])
        logging.debug("Found %i lint error%s", errors_count, 's' if errors_count > 1 else '')

    @timeable
    def config(self):
        """
        Dumps the configuration of peluche and its checkers to the .ini file

        Args:
            - None

        Returns:
            - None
        TODO
        """
        configuration = ConfigParser(allow_no_value=True)

        configuration.read_dict(self.get_config())

        for checker in BaseChecker.__subclasses__():
            checker_config = checker().get_config()

            configuration.read_dict(checker_config)

        configuration.write(open('peluche.ini', 'w'))

    def doc(self):
        """
        TODO
        """
        logging.debug("DOC with %s\n", self.args)

        command = ['pdoc']

        if self.args.force:
            command.append('--force')

        if self.args.live:
            command.extend(['--http', f"{self.args.host}:{self.args.port}"])
        else:
            command.extend(['--html', '--output-dir', self.args.output])

        command.append('peluche')

        subprocess.run(command)

    def get_config(self):
        configuration = dict()

        configuration['peluche'] = {}

        for key, value in self.OPTIONS.items():
            if value['help'] != '':
                configuration['peluche'][f"# {value['help'].strip()}"] = None

            configuration['peluche'][key] = value['default']

        return configuration
