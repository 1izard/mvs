import os

from renames import renames


TESTD0_PATH = os.path.join(os.path.dirname(__file__), 'testd0')


def test_glob_filenames():
    expected = ['tmpd0', 'tmpd1', 'tmpd2', 'tmp0.txt', 'tmp1.txt', 'tmp2.txt']
    expected.sort()

    actual = renames.glob_filenames(TESTD0_PATH)
    actual.sort()

    assert expected == actual
