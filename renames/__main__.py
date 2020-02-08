import argparse


def main():
    parser = argparse.ArgumentParser(description='Rename files at once',
                                     usage='Exec "$ renames" and edit file names like "src >> dst"')
    parser.parse_args()


if __name__ == '__main__':
    main()
