#!/usr/bin/env python3
import sys
from pathlib import Path
from subprocess import Popen, PIPE

def main(input_tar, output_diskimage, kernel_boot_params):
    input_tar_path = Path(input_tar)
    tar_size = input_tar_path.stat().st_size
    
    fudge_factor = 1.50
    mnt_dir = "/mnt"
    cmds = ([
        f"truncate -s 0 {output_diskimage} # erase any potential leftovers",
        f"truncate -s {int(tar_size * fudge_factor)} {output_diskimage}",
        f"mkfs.ext4 -L METALLIZE_ROOT {output_diskimage}",
        f"mkdir -p {mnt_dir}",
        f"mount {output_diskimage} {mnt_dir} -o loop",
        f"tar -C {mnt_dir} -xf {input_tar}",
        f"cp etc/isolinux.cfg {mnt_dir}/boot/extlinux.conf",
        f"sed -i 's|METALLIZE_LINUX_CMDLINE|{kernel_boot_params}|' {mnt_dir}/boot/extlinux.conf",
        f"extlinux --install /mnt/boot",
        f"umount {mnt_dir}",
    ])
    p = Popen(['/bin/sh', '-x', '-e'], stdin=PIPE)
    p.communicate(input="\n".join(cmds).encode("utf-8"))
    sys.exit(p.returncode)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], ' '.join(sys.argv[3:]))