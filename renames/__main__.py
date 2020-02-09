import argparse
import os
import sys

from renames import renames


FILELIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'filelist.txt')


def main():
    parser = argparse.ArgumentParser(description='Rename files at once',
                                     usage='Exec "$ renames" and edit file names like "src >> dst"')
    parser.parse_args()

    current_dir_path = os.getcwd()
    file_names = renames.glob_file_names(current_dir_path)
    if len(file_names) == 0:
        print('No files on current directory')
        sys.exit(1)

    file_names.sort()
    renames.write_file_names(file_names, FILELIST_PATH)

    status_code = renames.open_editor(FILELIST_PATH)
    if status_code != 0:
        sys.exit(1)

    file_list_lines = renames.read_file_list_lines(FILELIST_PATH)
    try:
        file_name_map = renames.build_file_name_map(file_list_lines)
    except ValueError as err:
        print(str(err))
        sys.exit(1)

    org_file_name_set = set(file_names)
    src_file_name_set = set(file_name_map.keys())
    if org_file_name_set != src_file_name_set:
        print('Rename suspended; do not edit src file names')
        sys.exit(1)

    renames.rename_files(file_name_map, current_dir_path)


if __name__ == '__main__':
    main()
