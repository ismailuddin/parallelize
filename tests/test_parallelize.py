"""
Module to run tests for parallelize.py
"""

import unittest
import random
from parallelize import parallelize
import pathlib


class TestParallelize(unittest.TestCase):
    """
    Class to test parallelize.parallelize functions
    """

    def test_make_divisions(self):
        for _ in range(5):
            items = list(range(random.randrange(300, 500)))
            splits = random.randrange(2, 18)
            divisions = parallelize.make_divisions(items, n_splits=splits)
            self.assertEqual(len(divisions) - 1, splits)

        with self.assertRaises(ValueError):
            parallelize.make_divisions([0, 1], 3)

    def test_retrieve_output(self):
        file_paths = []
        for i in range(1, 6):
            path = parallelize.write_output_to_temp_file('a' * i)
            file_paths.append(path)
        file_paths = [(i, path) for i, path in enumerate(file_paths)]
        results = parallelize.retrieve_output(file_paths)
        self.assertEqual(
            results,
            [
                (0, 'a'),
                (1, 'aa'),
                (2, 'aaa'),
                (3, 'aaaa'),
                (4, 'aaaaa')
            ]
        )

        for _, path in file_paths:
            self.assertFalse(pathlib.Path(path).exists())
