FROM ubuntu:20.04 as common_base

# facilitate apt cache
RUN --mount=type=cache,target=/var/cache/apt,id=ext4-generator \ 
    apt-get update && apt-get install --no-install-recommends -y \
    extlinux python3 e2fsprogs

COPY etc/isolinux.cfg /etc
COPY scripts/ext4.py /build.cmd