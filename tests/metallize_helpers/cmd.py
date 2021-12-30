import os
import logging
import subprocess
import time
import psutil
import json
from pathlib import Path
from metallize import load_config

def run(cmd):
    logging.info(cmd)
    os.system(cmd)

def popen(cmd, log_file):
    logging.info(cmd)
    return subprocess.Popen(cmd, start_new_session=True, stdout=log_file, stderr=log_file, shell=True)

class MetallizeTest:
    def __init__(self, test_file, src_config_name):
        test_path = Path(test_file)
        self.test_path = test_path.parent
        self.project_path = self.test_path.parent.parent
        self.src_config = self.project_path / 'profiles' / src_config_name
        self.metallize_logs = self.test_path / "metallize_logs.txt"
        self.uefi_logs = self.test_path / "build_uefi_logs.txt"
        self.build_path = self.test_path / 'build'
        self.output_image = self.build_path / 'filesystem.img'
        self.modified_config = self.build_path / (test_path.stem + '.json')

    def setup(self):
        run(f'rm -rf {self.uefi_logs} {self.metallize_logs}')
        os.makedirs(self.build_path, exist_ok=True)
    
    def cleanup(self):
        run(f'rm -rf {self.build_path}')
    
    def generate_config_from_template(self, modifier_f=lambda _ : ()):
        cfg = load_config(self.project_path, self.src_config, default_built_dir=str(self.build_path))
        cfg['output']['file'] = str(self.output_image)
        modifier_f(cfg)
        cfg_str = json.dumps(cfg, indent=4, sort_keys=True)
        logging.info(cfg_str)
        with open(self.modified_config, 'w') as cfg_out:
            cfg_out.write(cfg_str)
        return self.modified_config

    def run_metallize(self, extra_args = ''):
        run(f'cd {self.test_path} | {self.project_path}/metallize.py {self.modified_config} {extra_args} '
              f'| bash > {self.metallize_logs} 2>&1')
        assert(self.output_image.exists())

    def run_qemu(self, checker_f, legacy_or_uefi="legacy", timeout = 3 * 60):
        with open(self.uefi_logs, 'w') as log_file:
            p = popen(f"{self.project_path}/scripts/{legacy_or_uefi}-boot.sh {self.output_image}", log_file)
        self.pid = p.pid
        start_time = time.time()
        success = False
        while p.poll() is None and time.time() - start_time < timeout:
            time.sleep(5)
            success = checker_f(open(self.uefi_logs, "r").read())
            if success:
                break
        self.kill()
        assert success, "qemu failed or test timed out without expected output"

    def kill(self):
        process = psutil.Process(self.pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()