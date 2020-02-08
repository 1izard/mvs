import os
from typing import List
import subprocess
import traceback
import sys


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
        file_path {str} -- file path to be open by editor

    Returns:
        int -- status_code: {0: success, otherwise: failure}
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
