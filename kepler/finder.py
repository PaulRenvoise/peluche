import os
import glob
import logging
from itertools import combinations

from .tracer import tracer


class Finder():
    """
    TODO
    """
    def find_files(self, paths):
        """
        Orchestrates the search, normalization, deduplication, and filtering of files from a list of paths

        Handles environment variables (such as $HOME, $NAME, or $WHATEVER), '~', and symlinks

        Args:
            - paths (list<str>): the paths in which to find the files

        Returns:
            - list(<str>): the list of files found
        """
        with tracer('Finding files'):
            paths = self._normalize_paths(paths)

            paths = self._cleanup_paths(paths)

            files = self._expand_paths_to_files(paths)

            files = self._filter_files(files)

            logging.debug("  Found %i matching files!", len(files))


        return files

    def _normalize_paths(self, paths):
        return [os.path.realpath(os.path.expanduser(os.path.expandvars(path))) for path in paths]

    def _cleanup_paths(self, paths):
        sorted_paths = sorted(paths, key=len)

        non_nested_paths = set(sorted_paths)

        for index, lhs in enumerate(sorted_paths, 1):
            if os.path.isfile(lhs):
                continue

            for rhs in sorted_paths[index:]:
                if rhs.startswith(lhs) and rhs in non_nested_paths:
                    non_nested_paths.remove(rhs)

        logging.debug("  Discarded %i nested paths", len(paths) - len(non_nested_paths))

        return non_nested_paths

    def _expand_paths_to_files(self, paths):
        expanded_files = []

        for path in paths:
            if os.path.isfile(path):
                expanded_files.append(path)
                continue

            walked_paths = []
            for root, _dirs, _files in os.walk(path):
                if root.endswith('__pycache__'):
                    continue

                # TODO: handle more filetypes
                for globbed_file in glob.glob(os.path.join(root, '*.py')):
                    if globbed_file not in walked_paths:
                        walked_paths.append(globbed_file)

            expanded_files += walked_paths

        return expanded_files

    def _filter_files(self, files):
        return files
