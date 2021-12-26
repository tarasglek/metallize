FROM ubuntu:20.04 as common_base
# facilitate apt cache
RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN echo deb http://archive.ubuntu.com/ubuntu bionic-backports main restricted universe multiverse >> /etc/apt/sources.list
ARG DEBIAN_FRONTEND=noninteractive
ENV KERNEL 5.4.0-52-generic
RUN --mount=type=cache,target=/var/cache/apt,id=squashfs-and-syslinux-2 \ 
    apt-get update && apt-get install --no-install-recommends -y \
    mkisofs syslinux syslinux-utils syslinux-common isolinux p7zip-full curl ca-certificates wget
RUN mkdir -p /build
WORKDIR /build


RUN wget -O debian.iso -q --show-progress https://cdimage.debian.org/cdimage/archive/11.1.0/amd64/iso-cd/debian-11.1.0-amd64-netinst.iso && \
    7z x debian.iso -odebian_files && \
    mkdir -p /etc/grub && \
    mv 'debian_files/[BOOT]/2-Boot-NoEmul.img' /etc/grub/debian.efi.stub && \
    mv debian_files/EFI /etc/grub/EFI && \
    chmod -R  a+rx /etc/grub/EFI && \
    rm -fR debian_files debian.iso

# this controls compression settings for initrd and squashfs
COPY etc/* /etc
COPY scripts/build.sh /build.cmd
#Ubuntu 18.04 doesn't have isohybrid which we need to make isos bootable from hd
COPY --from=builder /usr/local/bin/*s*fs* /usr/local/bin/