import unittest

from complex_rest_dtcd_supergraph.utils import (
    homogeneous,
    savable_as_property,
    valid_property,
)


class TestUtils(unittest.TestCase):
    def test_valid_property(self):
        # int
        value = 42
        self.assertTrue(valid_property(value))

        # invalid: list
        value = [1, 2, 3]
        self.assertFalse(valid_property(value))

        # invalid: dict
        value = {"age": 42}
        self.assertFalse(valid_property(value))

    def test_is_homogeneous(self):
        seq = (1, 2, 3)
        self.assertTrue(homogeneous(seq))

        seq = (1.0, 2.4, 3.1)
        self.assertTrue(homogeneous(seq))

        seq = ("ham", "spam")
        self.assertTrue(homogeneous(seq))

        # empty sequence
        seq = []
        self.assertTrue(homogeneous(seq))

        # one member
        seq = (1,)
        self.assertTrue(homogeneous(seq))

        # non-homogeneous
        seq = (1, 2.5, "spam")
        self.assertFalse(homogeneous(seq))

    def test_savable_as_property(self):
        # valid
        # int
        value = 42
        self.assertTrue(savable_as_property(value))

        # empty list
        value = []
        self.assertTrue(savable_as_property(value))

        # list of ints
        value = [1, 2, 3]
        self.assertTrue(savable_as_property(value))

        # list of strs
        value = ["ham", "spam"]
        self.assertTrue(savable_as_property(value))

        # invalid
        # bad value type
        value = {"age": 42}
        self.assertFalse(savable_as_property(value))

        # list of non-homogeneous properties
        value = ["ham", 1, True]
        self.assertFalse(savable_as_property(value))

        # list of bad types
        value = [{"age": 42}, {"age": 17}]
        self.assertFalse(savable_as_property(value))
