import os
from typing import List, Tuple, Dict
import subprocess
import traceback
import sys
import re


FILE_LIST_LINE_PATTERN = re.compile(r'^\S+\s*?>>\s*?\S+$')
INVALID_CHAR_PATTERN = re.compile(r'.*(/).*')


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


def build_file_name_pair(file_list_line: str) -> Tuple[str, str] or None:
    """Build and return file name pair of src and dst.
    Return (src, dst) when file list line follows the correct format, otherwise retunr None.

    Arguments:
        file_list_line {str} - - file list line

    Returns:
        Tuple[str, str] or None - - (src, dst) or None
    """
    if INVALID_CHAR_PATTERN.match(file_list_line):
        return None
    res = FILE_LIST_LINE_PATTERN.fullmatch(file_list_line)
    if res:
        file_name_pair = res.group().split('>>')
        return (file_name_pair[0].strip(), file_name_pair[1].strip())
    else:
        return None


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
        res = build_file_name_pair(line)
        if res:
            file_name_map[res[0]] = res[1]
        else:
            err_msg = f'line {i}: Invalid syntax; {line}\n\
                Expected format is such as "src >> dst".'
            raise ValueError(err_msg)

    # check duplicate src file names
    if len(file_list_lines) != len(file_name_map):
        raise ValueError('Found a duplicate src file name. File name must be unique.')

    # check duplicate dst file names
    if has_duplicate_value(file_name_map):
        raise ValueError('Found a duplicate dst file name. File name must be unique.')

    return file_name_map
