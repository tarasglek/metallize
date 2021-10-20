# syntax = docker/dockerfile:1.2
# require buildkit ^
FROM ubuntu:trusty
# facilitate apt cache
RUN rm -f /etc/apt/apt.conf.d/docker-clean
# isohybrid not available in newer ubuntu
ARG DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,id=squashfs-and-syslinux-1 \
    apt-get update && apt-get install --no-install-recommends -y syslinux

FROM ubuntu:20.04 as common_base
# facilitate apt cache
RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN echo deb http://archive.ubuntu.com/ubuntu bionic-backports main restricted universe multiverse >> /etc/apt/sources.list
ARG DEBIAN_FRONTEND=noninteractive
ENV KERNEL 5.4.0-52-generic
RUN --mount=type=cache,target=/var/cache/apt,id=squashfs-and-syslinux-2 \ 
    apt-get update && apt-get install --no-install-recommends -y \
    mkisofs syslinux syslinux-common isolinux
RUN mkdir -p /build
WORKDIR /build

# This is an intermediate image for building things without bloating resulting image
FROM common_base as builder
RUN --mount=type=cache,target=/var/cache/apt,id=squashfs-and-syslinux-4 \ 
    apt-get update && apt-get install -y build-essential liblzma-dev liblz4-dev zlib1g-dev curl
ENV SQUASHFS_TAR 4.5.tar.gz
RUN curl -L https://github.com/plougher/squashfs-tools/archive/refs/tags/$SQUASHFS_TAR | tar -zxv
RUN cd squashfs-tools*/squashfs-tools && make LZ4_SUPPORT=1 LZMA_XZ_SUPPORT=1 XZ_SUPPORT=1 -j`nproc` && make install

FROM common_base

# this controls compression settings for initrd and squashfs
COPY etc/isolinux.cfg /root/
#Ubuntu 18.04 doesn't have isohybrid which we need to make isos bootable from hd
COPY --from=0 /usr/bin/isohybrid /usr/bin/isohybrid
COPY --from=builder /usr/local/bin/*s*fs* /usr/local/bin/


