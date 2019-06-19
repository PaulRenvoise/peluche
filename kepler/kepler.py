import os
from itertools import repeat
import logging
import subprocess
import multiprocessing as mp

from blinker import signal

from .__pkg__ import __version__
from .checkers import BaseChecker
from .checkers import *  # Registers the checkers as subclasses of BaseChecker
from .finder import Finder
from .progress import Progress
from .source import Source
from .store import Store
from .walker import Walker


class Kepler():
    """
    """
    def __init__(self, args, reporter=None, config=None):
        self.args = args

    def run(self):
        logging.debug("RUN with %s\n", self.args)

        checkers = [checker() for checker in BaseChecker.__subclasses__()]

        finder = Finder()

        progress = Progress(style='filename')
        progress.initialize()

        for f in progress.monitor(finder.find_files(self.args.paths)):
            # logging.debug(f)
            source = Source(f)
            # ap(source.fst)

            walker = Walker(source, checkers, None)
            walker.walk()

        progress.finalize()

    def config(self):
        logging.debug("CONFIG with %s\n", self.args)
        pass

    def doc(self):
        logging.debug("DOC with %s\n", self.args)

        command = ['pdoc']

        if self.args.force:
            command.append('--force')

        if self.args.live:
            command.extend(['--http', f"{self.args.host}:{self.args.port}"])
        else:
            command.extend(['--html', '--output-dir', self.args.output])

        command.append('kepler')

        subprocess.run(command)

    @property
    def version(self):
        print(__version__)
