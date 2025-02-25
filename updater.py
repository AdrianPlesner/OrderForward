import os
import sys


def main():
    old_exe = sys.argv[1]
    new_exe = sys.argv[2]
    os.remove(old_exe)
    os.replace(new_exe, old_exe)


if __name__ == "__main__":
    main()