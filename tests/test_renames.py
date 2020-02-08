import os

from renames import renames


TEST_PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), 'test_products')
TESTD0_PATH = os.path.join(os.path.dirname(__file__), 'testd0')


def test_glob_file_names():
    expected = ['tmpd0', 'tmpd1', 'tmpd2', 'tmp0.txt', 'tmp1.txt', 'tmp2.txt']
    expected.sort()

    actual = renames.glob_file_names(TESTD0_PATH)
    actual.sort()

    assert expected == actual


def test_write_file_names():
    file_names = ['tmpd0', 'tmpd1', 'tmpd2', 'tmp0.txt', 'tmp1.txt', 'tmp2.txt']

    expected = ['tmpd0 >> ', 'tmpd1 >> ', 'tmpd2 >> ',
                'tmp0.txt >> ', 'tmp1.txt >> ', 'tmp2.txt >> ']
    expected.sort()

    dst_path = os.path.join(TEST_PRODUCTS_PATH, 'test_write_file_names_result.txt')
    renames.write_file_names(file_names, dst_path)

    with open(dst_path, 'r') as f:
        lines = [l.strip('\n') for l in f]

    actual = sorted(lines)
    assert expected == actual
