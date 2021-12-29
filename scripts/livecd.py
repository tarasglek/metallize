#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT

def main(dry_run:bool, input_tar, output_diskimage, kernel_boot_params):
    iso_src_path = Path("/tmp") / "iso_src"
    squashfs_file = iso_src_path / "live" / f"rootfs.squashfs"
    boot_path = iso_src_path / "isolinux"
    grub_path = boot_path / "grub/x86_64-efi/"
    # wonder if this can be a directory
    grub_search = iso_src_path / ".disk/info"

    compression = "lz4"
    cmds = [
        f"sed -i 's|METALLIZE_LINUX_CMDLINE|boot=live {kernel_boot_params}|' /etc/grub.cfg /etc/isolinux.cfg",
        f"mkdir -p {squashfs_file.parent} {boot_path} {grub_path} {grub_search.parent}",
        f"echo MetallizeOS > {grub_search}",
        f"cp /etc/grub.cfg {grub_path}",
        f"cp -rT /etc/grub/EFI {iso_src_path}/EFI/",
        f"cp /etc/grub/debian.efi.stub {iso_src_path}/efi.img",
        f"cp /etc/isolinux.cfg /usr/lib/ISOLINUX/isolinux.bin /usr/lib/syslinux/modules/bios/ldlinux.c32 {boot_path}",

        f"tar --wildcards --delete 'boot/*' < {input_tar} | mksquashfs - {squashfs_file}  -comp {compression} -b 1024K -always-use-fragments -keep-as-directory -no-recovery -exit-on-error -tar",
        (
	        f"tar --show-transformed-names --transform='s:-.*::' --transform='s:.*/::' -xvf {input_tar} -C {boot_path} "
		    '--wildcards "boot/vmlinuz-*" '
		    '--wildcards "boot/initrd*-*"'
        ),
        f"mkisofs -o {output_diskimage} -J -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table  -eltorito-alt-boot -eltorito-boot efi.img -no-emul-boot {iso_src_path}",
        f"isohybrid {output_diskimage}",
        f"find {iso_src_path}"
    ]
    script = "\n".join(cmds)
    if dry_run:
        print(script)
        return
    p = Popen(['/bin/sh', '-x', '-e'], stdin=PIPE)
    p.communicate(input=script.encode("utf-8"))
    sys.exit(p.returncode)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args, rest_of_args = parser.parse_known_args()
    main(args.dry_run, rest_of_args[0], rest_of_args[1], ' '.join(rest_of_args[2:]))