import os
import time
import subprocess
import pytest
import psutil
from tests.metallize_helpers import cmd
from pathlib import Path

test_path = os.path.dirname(os.path.realpath(__file__))
project_path = test_path.split("tests/")[0]
metallize_logs = test_path + "/metallize_logs.txt"
uefi_logs = test_path + "/build_uefi_logs.txt"
livecd_iso = Path(test_path) / 'build/livecd.iso'

@pytest.fixture
def cleanup():
    yield
    cmd.run(f'rm -rf {test_path}/build')

def test_build_from_ext_dir(cleanup):
    cmd.run(f'rm -rf {uefi_logs} {metallize_logs}')
    cmd.run(f'cd {test_path} | {project_path}/metallize.py {test_path}/ubuntu20-livecd.iso.yaml --extensions_dir={test_path} '
              f'| bash > {metallize_logs} 2>&1')

    with open(metallize_logs, 'r') as log_file:
        lines = log_file.readlines()
        assert(livecd_iso.exists())

    with open(uefi_logs, 'w') as log_file:
        p = cmd.popen(f"{project_path}/scripts/uefi-boot.sh {livecd_iso}", log_file)

    start_time = time.time()
    while p.poll() is None and time.time() - start_time < 3 * 60:
        time.sleep(5)
        a_file = open(uefi_logs, "r")
        lines = a_file.readlines()

        if lines and lines[-1].find('test-host login') != -1:
            kill(p.pid)
            assert True
            break
    else:
        kill(p.pid)
        assert False

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


    # /home/parallels/Desktop/metallize/metallize/metallize.py /home/parallels/Desktop/metallize/metallize/profiles/ubuntu20-livecd.iso.yaml --extensions_dir=/home/parallels/test-plugin | bash