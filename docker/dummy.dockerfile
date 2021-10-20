ARG SRC_IMG=latest
FROM ${SRC_IMG}

ENV KERNEL 5.4.0-52-generic
RUN --mount=type=cache,target=/var/cache/apt,id=dummy \
    apt update && apt install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
     live-boot live-boot-initramfs-tools linux-image-$KERNEL linux-modules-extra-$KERNEL  systemd-sysv
