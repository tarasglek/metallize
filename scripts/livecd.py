#!/usr/bin/env python3
import sys
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT

def build_squashfs(config, tar_file: Path, squashfs_file: Path, images_path: Path, project_path: Path):
    live_path = squashfs_file.parent
    generator = config['output']['generator']
    cmds = [
        f"mkdir -p {live_path}",
        f"DOCKER_BUILDKIT=1 docker build -t {generator} -f {images_path / generator} {project_path}",
        f"rm -f {squashfs_file}",
	    (
            f"tar --wildcards --delete 'boot/*' < {tar_file} | "
            f"docker run -i -v {live_path.absolute()}:/tmp {USER_VAR} {generator} "
            f"mksquashfs - /tmp/{squashfs_file.name}  -comp {config['args']['compression']} -b 1024K -always-use-fragments -keep-as-directory -no-recovery -exit-on-error -tar "
        )
    ]
    return cmds

def extract_kernel_files(boot_path: Path, tar_file: Path):
    cmds = [
        f"mkdir -p {boot_path}",
        (
	        f"tar --show-transformed-names --transform='s:-.*::' --transform='s:.*/::' -xvf {tar_file} -C {boot_path} "
		    '--wildcards "boot/vmlinuz-*" '
		    '--wildcards "boot/initrd*-*"'
        )
    ]
    return cmds


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
    script = "\n".join(cmds)
    print(script)
    # p = Popen(['/bin/sh', '-x', '-e'], stdin=PIPE)
    # p.communicate(input=script.encode("utf-8"))
    # sys.exit(p.returncode)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], ' '.join(sys.argv[3:]))