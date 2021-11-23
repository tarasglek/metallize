ARG METALLIZE_SRC_IMG
FROM ${METALLIZE_SRC_IMG}

ENV KERNEL 5.4.0-52-generic
ARG METALLIZE_COMPRESSION
# COPY etc/initramfs.conf /etc/initramfs-tools/initramfs.conf
# RUN sed -i "s:lz4:$METALLIZE_COMPRESSION:" /etc/initramfs-tools/initramfs.conf
RUN --mount=type=cache,target=/var/cache/apt,id=dummy \
    apt-get update && apt install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
      live-boot live-boot-initramfs-tools linux-image-$KERNEL linux-modules-extra-$KERNEL  systemd-sysv sudo netplan.io
COPY etc/all-dhcp.yaml /etc/netplan
