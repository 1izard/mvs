import pytest
import os

from renames import renames


TEST_PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), 'test_products')
TESTD0_PATH = os.path.join(os.path.dirname(__file__), 'testd0')
TESTD1_PATH = os.path.join(os.path.dirname(__file__), 'testd1')


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


def test_read_file_lines():
    expected = [
        'src1 >> dst1',
        'src2 >> dst2',
        'src3 >> dst3',
    ]

    actual = renames.read_file_list_lines(os.path.join(TESTD1_PATH, 'filelist.txt'))
    actual

    assert expected == actual


def test_build_file_name_pair_valid():
    expected = ('src1', 'dst1')
    arg = 'src1 >> dst1'
    actual = renames.build_file_name_pair(arg)
    assert expected == actual


def test_build_file_name_pair_invalid_char():
    expected = None
    args = ['/src1 >> dst1', 'src1 >> /dst1']
    for arg in args:
        actual = renames.build_file_name_pair(arg)
        assert expected == actual


def test_build_file_name_pair_invalid_syntax():
    expected = None
    args = ['src1 > dst1', 'src 1 >> dst1']
    for arg in args:
        actual = renames.build_file_name_pair(arg)
        assert expected == actual


def test_has_duplicate_value_true():
    expected = True
    arg = {
        'src1': 'dst1',
        'src2': 'dst1',
    }
    actual = renames.has_duplicate_value(arg)

    assert expected == actual


def test_has_duplicate_false():
    expected = False
    arg = {
        'src1': 'dst1',
        'src2': 'dst2',
    }
    actual = renames.has_duplicate_value(arg)

    assert expected == actual


def test_build_file_name_map_valid():
    expected = {
        'src1': 'dst1',
        'src2': 'dst2'
    }

    arg = ['src1 >> dst1', 'src2 >> dst2']
    actual = renames.build_file_name_map(arg)

    assert expected == actual


def test_build_file_name_map_with_invalid_syntax():
    with pytest.raises(ValueError) as excinfo:
        arg = ['src1 > dst1', 'src2 > dst2']
        renames.build_file_name_map(arg)

    assert 'line 1: Invalid syntax;' in str(excinfo.value)


def test_build_file_name_map_with_duplicate_src():
    with pytest.raises(ValueError) as excinfo:
        arg = ['src1 >> dst1', 'src1 >> dst2']
        renames.build_file_name_map(arg)

    assert 'Found a duplicate src file name' in str(excinfo.value)


def test_build_file_name_map_with_duplicate_dst():
    with pytest.raises(ValueError) as excinfo:
        arg = ['src1 >> dst1', 'src2 >> dst1']
        renames.build_file_name_map(arg)

    assert 'Found a duplicate dst file name' in str(excinfo.value)
