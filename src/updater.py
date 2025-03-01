import os
import signal
import subprocess
import sys
from time import localtime, strftime, time


def main():
    parent_pid = int(sys.argv[1])
    print(f"killing {parent_pid}")
    try:
        os.kill(parent_pid, signal.SIGTERM)
    except Exception as e:
        print("Parent process already terminated")
    old_exe = sys.argv[2]
    new_exe = sys.argv[3]
    print("replacing file")
    try:
        os.remove(old_exe)
        os.replace(new_exe, old_exe)
        print("file replaced")
        subprocess.Popen(old_exe, shell=True)
    except Exception as e:
        print(f"An error occurred while updating: {e}")
        with open(os.path.join(os.getcwd(),"errorLog" + str(strftime("%Y/%B/%D-%H:%M:%S", localtime(time()))) + ".txt"), 'w') as f:
            f.write(f'{e}')


if __name__ == "__main__":
    main()