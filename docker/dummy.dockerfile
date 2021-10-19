ARG SRC_IMG=latest
FROM ${SRC_IMG}

ENV KERNEL 5.4.0-52-generic
RUN --mount=type=cache,target=/var/cache/apt,id=dummy \
    apt update && apt install -y linux-image-$KERNEL linux-modules-extra-$KERNEL
