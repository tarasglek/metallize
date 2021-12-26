ARG METALLIZE_SRC_IMG
FROM ${METALLIZE_SRC_IMG}

COPY etc/hosts /etc/
COPY etc/hostname /etc/
