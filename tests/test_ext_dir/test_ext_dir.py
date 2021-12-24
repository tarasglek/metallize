import os
import time
import subprocess
import pytest
import psutil
import logging
LOGGER = logging.getLogger(__name__)

project_path = os.path.realpath(__file__).split("tests/")[0]
test_path = os.path.dirname(os.path.realpath(__file__))
metallize_logs = test_path + "/metallize_logs.txt"
uefi_logs = test_path + "/build_uefi_logs.txt"


def run(cmd):
    LOGGER.info(cmd)
    os.system(cmd)

@pytest.fixture
def build():
    run(f'rm -rf {uefi_logs} {metallize_logs}')
    run(f'cd {test_path} | {project_path}/metallize.py {test_path}/ubuntu20-livecd.iso.yaml --extensions_dir={test_path} '
              f'| bash > {metallize_logs} 2>&1')

    yield
    run(f'rm -rf {test_path}/build')

def test_build_from_ext_dir(build):
    with open(metallize_logs, 'r') as log_file:
        lines = log_file.readlines()

        if not lines or lines[-1].find('/out/livecd.iso') == -1:
            assert False
            return

    with open(uefi_logs, 'w') as log_file:
        p = subprocess.Popen([f"{project_path}/scripts/uefi-boot.sh", f"{test_path}/build/livecd.iso"],
                             start_new_session=True, stdout=log_file, stderr=log_file)

    start_time = time.time()
    while time.time() - start_time < 3 * 60:
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