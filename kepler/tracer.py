import os
import logging
import time

from contextlib import contextmanager

with open(os.path.join(os.path.dirname(__file__), 'verbs.csv'), 'r') as verbs_file:
    VERBS = dict(line.split(',') for line in verbs_file.read().splitlines())


@contextmanager
def tracer(log):
    verb, _ = log.split(' ', 1)

    logging.info("%s...", log)

    before = time.time()

    yield

    logging.debug("%s in %fs", log.replace(verb, VERBS[verb]), time.time() - before)
