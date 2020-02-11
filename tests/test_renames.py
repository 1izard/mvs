import pytest
import os
import pathlib
import shutil

from renames import renames

HERE = os.path.dirname(os.path.abspath(__file__))

TEST_PRODUCTS_PATH = os.path.join(HERE, 'test_products')
TESTD0_PATH = os.path.join(HERE, 'testd0')
TESTD1_PATH = os.path.join(HERE, 'testd1')
TESTD2_PATH = os.path.join(HERE, 'testd2')


def set_test_files():
    if os.path.isdir(TESTD2_PATH):
        shutil.rmtree(TESTD2_PATH)
    os.makedirs(TESTD2_PATH)
    for i in range(3):
        inner_dir_path = os.path.join(TESTD2_PATH, f'tmpd2_{i}')
        os.makedirs(inner_dir_path)
        inner_file_path = os.path.join(TESTD2_PATH, f'tmp2_{i}.txt')
        with open(inner_file_path, 'w') as f:
            f.write(str(os.path.basename(inner_file_path)))
        for j in range(3):
            pathlib.Path(os.path.join(inner_dir_path, f'tmp2_{i}_{j}.txt')).touch()


def test_glob_file_names():
    expected = ['tmpd0', 'tmpd1', 'tmpd2', 'tmp0.txt', 'tmp1.txt', 'tmp2.txt']
    expected.sort()

    actual = renames.glob_file_names(TESTD0_PATH)
    actual.sort()

    assert actual == expected


def test_write_file_names():
    file_names = ['tmpd0', 'tmpd1', 'tmpd2', 'tmp0.txt', 'tmp1.txt', 'tmp2.txt']

    expected = ['tmpd0 >> tmpd0', 'tmpd1 >> tmpd1', 'tmpd2 >> tmpd2',
                'tmp0.txt >> tmp0.txt', 'tmp1.txt >> tmp1.txt', 'tmp2.txt >> tmp2.txt']
    expected.sort()

    dst_path = os.path.join(TEST_PRODUCTS_PATH, 'test_write_file_names_result.txt')
    renames.write_file_names(file_names, dst_path)

    with open(dst_path, 'r') as f:
        lines = [l.strip('\n') for l in f]

    actual = sorted(lines)
    assert actual == expected


def test_read_file_lines():
    expected = [
        'src1 >> dst1',
        'src2 >> dst2',
        'src3 >> dst3',
    ]

    actual = renames.read_file_list_lines(os.path.join(TESTD1_PATH, 'filelist.txt'))
    actual

    assert actual == expected


def test_build_file_name_pair_valid():
    expected = ('src1', 'dst1')
    arg = 'src1 >> dst1'
    actual = renames.build_file_name_pair(arg)
    assert actual == expected


def test_build_file_name_pair_with_invalid_char_slash():
    args = ['/src1 >> dst1', 'src1 >> /dst1']
    for i, arg in enumerate(args, 1):
        with pytest.raises(ValueError) as excinfo:
            renames.build_file_name_pair(arg)
        assert 'line {}: Invalid character' in str(excinfo.value)


def test_build_file_name_pair_with_invalid_char_single_quote():
    arg = "'/src1' >> dst1"
    with pytest.raises(ValueError) as excinfo:
        renames.build_file_name_pair(arg)
    assert 'line {}: Invalid character' in str(excinfo.value)


def test_build_file_name_pair_with_invalid_char_double_quote():
    arg = '"/src1" >> dst1'
    with pytest.raises(ValueError) as excinfo:
        renames.build_file_name_pair(arg)
    assert 'line {}: Invalid character' in str(excinfo.value)


def test_build_file_name_pair_invalid_syntax():
    args = ['src1 > dst1', 'src 1 >> dst1']
    for arg in args:
        with pytest.raises(ValueError) as excinfo:
            renames.build_file_name_pair(arg)
        assert 'line {}: Invalid syntax' in str(excinfo.value)


def test_has_duplicate_value_true():
    expected = True
    arg = {
        'src1': 'dst1',
        'src2': 'dst1',
    }
    actual = renames.has_duplicate_value(arg)

    assert actual == expected


def test_has_duplicate_false():
    expected = False
    arg = {
        'src1': 'dst1',
        'src2': 'dst2',
    }
    actual = renames.has_duplicate_value(arg)

    assert actual == expected


def test_build_file_name_map_valid():
    expected = {
        'src1': 'dst1',
        'src2': 'dst2'
    }

    arg = ['src1 >> dst1', 'src2 >> dst2']
    actual = renames.build_file_name_map(arg)

    assert actual == expected


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


def test_rename_files_normal():
    set_test_files()

    file_name_map = {
        'tmpd2_0': 'afterd2_0',
        'tmpd2_1': 'afterd2_1',
        'tmpd2_2': 'afterd2_2',
        'tmp2_0.txt': 'after2_0',
        'tmp2_1.txt': 'after2_1',
        'tmp2_2.txt': 'after2_2',
    }
    expected = set(file_name_map.values())

    renames.rename_files(file_name_map, TESTD2_PATH)

    with os.scandir(TESTD2_PATH) as it:
        actual = set([e.name for e in it])

    assert actual == expected


def test_rename_files_node():
    set_test_files()

    file_name_map = {
        'tmpd2_0': 'tmpd2_1',
        'tmpd2_1': 'tmpd2_2',
        'tmpd2_2': 'tmpd2_3',
        'tmp2_0.txt': 'tmp2_1.txt',
        'tmp2_1.txt': 'tmp2_2.txt',
        'tmp2_2.txt': 'tmp2_3.txt',
    }
    expected = set(file_name_map.values())

    renames.rename_files(file_name_map, TESTD2_PATH)

    with os.scandir(TESTD2_PATH) as it:
        actual = set([e.name for e in it])

    assert actual == expected


def test_rename_files_cycle():
    set_test_files()

    file_name_map = {
        'tmpd2_0': 'tmpd2_1',
        'tmpd2_1': 'tmpd2_2',
        'tmpd2_2': 'tmpd2_0',
        'tmp2_0.txt': 'tmp2_1.txt',
        'tmp2_1.txt': 'tmp2_2.txt',
        'tmp2_2.txt': 'tmp2_0.txt',
    }
    expected = set(file_name_map.values())

    renames.rename_files(file_name_map, TESTD2_PATH)

    with os.scandir(TESTD2_PATH) as it:
        actual = set([e.name for e in it])

    assert actual == expected


def test_rename_files_cycle_pair():
    set_test_files()

    file_name_map = {
        'tmpd2_0': 'tmpd2_1',
        'tmpd2_1': 'tmpd2_0',
        'tmpd2_2': 'tmpd2_2',
        'tmp2_0.txt': 'tmp2_1.txt',
        'tmp2_1.txt': 'tmp2_0.txt',
        'tmp2_2.txt': 'tmp2_2.txt',
    }
    expected = set(file_name_map.values())

    renames.rename_files(file_name_map, TESTD2_PATH)

    with os.scandir(TESTD2_PATH) as it:
        actual = set([e.name for e in it])

    assert actual == expected


def test_rename_files_including_same():
    set_test_files()

    file_name_map = {
        'tmpd2_0': 'tmpd2_0',
        'tmpd2_1': 'tmpd2_1',
        'tmpd2_2': 'tmpd2_3',
        'tmp2_0.txt': 'tmp2_0.txt',
        'tmp2_1.txt': 'tmp2_1.txt',
        'tmp2_2.txt': 'tmp2_3.txt',
    }

    expected = set(file_name_map.values())

    renames.rename_files(file_name_map, TESTD2_PATH)

    with os.scandir(TESTD2_PATH) as it:
        actual = set([e.name for e in it])

    assert actual == expected
