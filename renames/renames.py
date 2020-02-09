import os
from typing import List, Tuple, Dict
import subprocess
import traceback
import sys
import re
from collections import deque, namedtuple
import tempfile


FILE_LIST_LINE_PATTERN = re.compile(r'^\S+\s*?>>\s*?\S+$')
INVALID_CHAR_PATTERN = re.compile(r'.*(/|\"|\').*')


def glob_file_names(dir_path: str) -> List[str]:
    with os.scandir(dir_path) as it:
        file_names = [e.name for e in it]
    return file_names


def write_file_names(file_names: List[str], dst_path: str):
    with open(dst_path, 'w') as f:
        lines = [f'{file_name} >> ' for file_name in file_names]
        f.write('\n'.join(lines))


def open_editor(file_path: str) -> int:
    """Open default editor

    Arguments:
        file_path {str} - - file path to be open by editor

    Returns:
        int - - status_code: {0: success, otherwise: failure}
    """
    status_code = 0

    editor = os.getenv('EDITOR')
    if editor is None:
        editor = 'vi'

    try:
        subprocess.run([editor, file_path])
    except subprocess.SubprocessError:
        print('Error!')
        print('Process suspended')
        print('=' * 80)
        traceback.print_exc(file=sys.stdout)
        print('=' * 80)
        status_code = 1

    return status_code


def read_file_list_lines(file_path: str) -> List[str]:
    """Read file list lines from file list txt file

    Arguments:
        file_path {str} - - path of file list txt

    Returns:
        List[str] - - file list lines
    """
    with open(file_path, 'r') as f:
        lines = [l.strip() for l in f]
        return lines


def build_file_name_pair(file_list_line: str) -> Tuple[str, str]:
    """Build and return file name pair of src and dst.
    Return (src, dst) when file list line follows the correct format, otherwise retunr None.

    Arguments:
        file_list_line {str} - - file list line

    Returns:
        Tuple[str, str] - - (src, dst)
    """
    if INVALID_CHAR_PATTERN.match(file_list_line):
        raise ValueError('line {}: Invalid character; ' + file_list_line)
    res = FILE_LIST_LINE_PATTERN.fullmatch(file_list_line)
    if res:
        file_name_pair = res.group().split('>>')
        return (file_name_pair[0].strip(), file_name_pair[1].strip())
    else:
        raise ValueError('line {}: Invalid syntax; ' + file_list_line +
                         '\n' + 'Expected format is such as "src" >> dst".')


def has_duplicate_value(mp: Dict[str, str]) -> bool:
    v_set = set((v for v in mp.values()))
    return len(v_set) != len(mp)


def build_file_name_map(file_list_lines: List[str]) -> Dict[str, str]:
    """Build and return map of file name.
    If found invalid syntax, return None.

    Arguments:
        file_list_lines {List[str]} - - lines of file list

    Returns:
        Dict[str, str] or None - - file name map. key is src file name, value is dst file name.
    """
    file_name_map = {}
    for i, line in enumerate(file_list_lines, 1):
        try:
            res = build_file_name_pair(line)
            file_name_map[res[0]] = res[1]
        except ValueError as err:
            raise ValueError(str(err).format(i))

    # check duplicate src file names
    if len(file_list_lines) != len(file_name_map):
        raise ValueError('Found a duplicate src file name. File name must be unique.')

    # check duplicate dst file names
    if has_duplicate_value(file_name_map):
        raise ValueError('Found a duplicate dst file name. File name must be unique.')

    return file_name_map


def rename_files(file_name_map: Dict[str, str], dir_path: str):
    flag_map = {k: False for k in file_name_map.keys()}
    Node = namedtuple('Node', ('src', 'dst'))
    node_stack: List[Node] = deque()

    for src_file_name, dst_file_name in file_name_map.items():
        if flag_map[src_file_name]:
            continue

        node_stack.append(Node(src_file_name, dst_file_name))
        flag_map[src_file_name] = True

        while (dst_file_name in file_name_map) and (flag_map[dst_file_name] is False):
            node_stack.append(Node(dst_file_name, file_name_map[dst_file_name]))
            flag_map[dst_file_name] = True
            dst_file_name = file_name_map[dst_file_name]

        # save head node file temporarily for cycle
        head_node = node_stack.pop()
        with tempfile.NamedTemporaryFile() as f:
            tmpfile_path = f.name
        os.rename(os.path.join(dir_path, head_node.src), tmpfile_path)

        while len(node_stack) > 0:
            node = node_stack.pop()
            os.rename(os.path.join(dir_path, node.src), os.path.join(dir_path, node.dst))

        os.rename(tmpfile_path, os.path.join(dir_path, head_node.dst))
