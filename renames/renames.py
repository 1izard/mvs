import os
from typing import List


def glob_filenames(dir_path: str) -> List[str]:
    with os.scandir(dir_path) as it:
        filenames = [e.name for e in it]
    return filenames
