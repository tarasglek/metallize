"""
metallize.py config.yaml
"""

import yaml
import sys
def main(config_file):
    config = yaml.load(open(config_file), Loader=yaml.SafeLoader)
    print(config)

if __module__ == '__main__':
    config_file = sys.argv[-1]
    main(config_file)
    