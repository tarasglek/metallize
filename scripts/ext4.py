#!/usr/bin/env python3
import sys
from pathlib import Path

def main(input_tar, output_diskimage):
    input_tar_path = Path(input_tar)
    tar_size = input_tar_path.stat().st_size
    
    fudge_factor = 1.50
    mnt_dir_path = Path(input_tar + ".mnt")
    mnt_dir = mnt_dir_path.resolve()
    print(f"umount -l {output_diskimage}")
    print(f"rm -f {output_diskimage} {mnt_dir}")
    print(f"truncate -s {int(tar_size * fudge_factor)} {output_diskimage}")
    print(f"mkfs.ext4 {output_diskimage}")
    print(f"mkdir -p {mnt_dir}")
    print(f"sudo mount {output_diskimage} {mnt_dir} -o loop")
    print(f"sudo tar -C {mnt_dir} -xvf {input_tar}")
    print(f"sudo cp etc/isolinux.cfg {mnt_dir}/boot/extlinux.conf")
    print(f"docker run -v  {mnt_dir}:/mnt  --privileged squashfs-and-syslinux.dockerfile extlinux --install /mnt/boot")
    print(f"sudo umount {mnt_dir}")
    print(f"rm -r {mnt_dir}")
    

if __name__ == '__main__':
    main(sys.argv[-2], sys.argv[-1])