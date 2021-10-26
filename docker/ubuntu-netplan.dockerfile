ARG METALLIZE_SRC_IMG
FROM ${METALLIZE_SRC_IMG}

ENV KERNEL 5.4.0-52-generic
RUN --mount=type=cache,target=/var/cache/apt \
    apt update && apt install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
      netplan.io
COPY etc/all-dhcp.yaml /etc/netplan
