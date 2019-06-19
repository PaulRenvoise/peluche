import os
import glob
import time
from itertools import combinations


class Finder():
    def find_files(self, paths):
        """
        Orchestrates the normalization and near-deduplication of paths,
        as well as the finding and filtering of files from a list of paths
        """
        before = time.time()

        paths = self._normalize_paths(paths)
        print(paths)

        paths = self._cleanup_paths(paths)
        print(paths)

        files = self._expand_paths_to_files(paths)
        print(len(files))

        print(f"{time.time() - before}")
        return []

        files = self._filter_files(files)

        return files

    def _normalize_paths(self, paths):
        """
        Normalizes paths to return their absolute fully expanded form

        - `.expandvars()` handles environment variables (such as $HOME, $NAME, or $WHATEVER)
        - `.expanduser()` handles '~'
        - `.realpath()` resolves simlink AND the absolute path (just like `.abspath()`)

        Args:
            - paths (list<str>) : the paths to normalize

        Returns:
            - list<str> : the absolute expanded paths
        """
        return [os.path.realpath(os.path.expanduser(os.path.expandvars(path))) for path in paths]

    def _cleanup_paths(self, paths):
        """
        Removes redundant paths, such as duplicates, or paths that are nested in at least another path

        Args:
            - paths (list<str>) : the paths to cleanup

        Returns:
            - list<str> : the cleaned up paths
        """
        sorted_paths = sorted(paths, key=len)
        non_nested_paths = set([sorted_paths[0]])  # first path is the shortest so it MUST be processed

        for index, lhs in enumerate(sorted_paths):
            if os.path.isfile(lhs):
                continue

            for rhs in sorted_paths[index:]:
                if not rhs.startswith(lhs):
                    non_nested_paths.update([rhs])

        return non_nested_paths

    def _expand_paths_to_files(self, paths):
        """
        Recursively extracts the files from the paths

        Args:
            - paths (list<str>) : the paths to extract the files from

        Returns:
            - list<str> : the files extracted from the paths
        """
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
        """
        Filters unwanted files (following a config) from a given set of files

        Args:
            - files (list<str>) : the list of files to reduce

        Returns:
            - list<str> : the filtered list of files
        """
        return files
