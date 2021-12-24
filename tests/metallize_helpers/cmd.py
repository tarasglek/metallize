import os
import logging
import subprocess

def run(cmd):
    logging.info(cmd)
    os.system(cmd)

def popen(cmd, log_file):
    logging.info(cmd)
    return subprocess.Popen(cmd, start_new_session=True, stdout=log_file, stderr=log_file, shell=True)
