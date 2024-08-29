import time
import glob
from pathlib import Path


def poll_files(directory: str):
    file_path = Path(directory)
    file_path_pattern = file_path.joinpath('*.LOG')
    # print(file_path_pattern)
    # f'{file_path}\\*.LOG'
    files = glob.iglob(f'{file_path_pattern}')
    counter = 0
    while not files and counter < 20:
        time.sleep(1)
        counter += 1
        files = glob.iglob(f'{file_path_pattern}')

    if not files:
        return
    files_sorted = sorted(files, key=lambda x: Path(x).stat().st_mtime)
    # for file in files_sorted:
    #     print(file)

    return files_sorted[-1]


# current = Path(__file__).parent.parent
# log_path = current.joinpath('system_logs')
# poll_files(log_path)
