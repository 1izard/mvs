import argparse
import os

from renames import renames


def main():
    parser = argparse.ArgumentParser(description='Rename files at once',
                                     usage='Exec "$ renames" and edit file names like "src >> dst"')
    parser.parse_args()

    status_code = renames.open_editor(os.path.join(os.path.dirname(__file__), 'filelist.txt'))


if __name__ == '__main__':
    main()
