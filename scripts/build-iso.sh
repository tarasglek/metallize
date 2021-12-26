#!/bin/sh
set -x -e
ISO_SRC_DIR=/iso_src/
ISO_BOOT_DIR=$ISO_SRC_DIR/isolinux
EFI_STUB=/etc/grub/debian.efi.stub
GRUB_DIR=$ISO_SRC_DIR/boot/grub/x86_64-efi/
GRUB_SEARCH=$ISO_SRC_DIR/.disk/info
LINUX_CMDLINE='initrd=initrd.img boot=live nomodeset console=ttyS0,115200 console=tty0'

mkdir -p $ISO_BOOT_DIR
cp /boot/vmlinuz /boot/initrd.img $ISO_BOOT_DIR
cp /usr/lib/ISOLINUX/isolinux.bin /usr/lib/syslinux/modules/bios/ldlinux.c32 $ISO_BOOT_DIR
cp /etc/isolinux.cfg $ISO_BOOT_DIR
mkdir -p $GRUB_DIR `dirname $GRUB_SEARCH`
echo MetallizeOS > $ISO_SRC_DIR/.disk/info
cp /etc/grub.cfg $GRUB_DIR
cp -rT /etc/grub/EFI $ISO_SRC_DIR/EFI/
# EFI stub is based on grub one borrowed from debian installer. If one looks into embedded debian/grub.cfg, however grub seems to pick the grub.cfg on cdrom usually, so it contains an identical one
# this causes us to have a /.disk/info file and ./boot/grub/x86_64-efi/grub.cfg
cp $EFI_STUB $ISO_SRC_DIR/efi.img
sed -i "s/METALLIZE_LINUX_CMDLINE/$LINUX_CMDLINE/" $GRUB_DIR/grub.cfg $ISO_BOOT_DIR/isolinux.cfg
mkisofs -o /out/$1 -J -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table  -eltorito-alt-boot -eltorito-boot efi.img -no-emul-boot $ISO_SRC_DIR

isohybrid /out/livecd.iso
