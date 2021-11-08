#!/bin/sh
set -x -e
ISO_SRC_DIR=/iso_src/
ISO_BOOT_DIR=$ISO_SRC_DIR/isolinux
mkdir -p $ISO_BOOT_DIR
cp /boot/vmlinuz /boot/initrd.img $ISO_BOOT_DIR
cp /usr/lib/ISOLINUX/isolinux.bin /usr/lib/syslinux/modules/bios/ldlinux.c32 $ISO_BOOT_DIR

cp /etc/isolinux.cfg $ISO_BOOT_DIR
mkisofs -o /out/$1 -J -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table $ISO_SRC_DIR

# todo: use bootctl to generate efiboot.img, then follow instructions from https://wiki.syslinux.org/wiki/index.php?title=Isohybrid
# isohybrid --uefi /out/livecd.iso
isohybrid /out/livecd.iso
