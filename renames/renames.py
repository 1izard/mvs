import os
from typing import List


def glob_file_names(dir_path: str) -> List[str]:
    with os.scandir(dir_path) as it:
        file_names = [e.name for e in it]
    return file_names


def write_file_names(file_names: List[str], dst_path: str):
    with open(dst_path, 'w') as f:
        lines = [f'{file_name} >> ' for file_name in file_names]
        f.write('\n'.join(lines))
