ARG METALLIZE_SRC_IMG
FROM ${METALLIZE_SRC_IMG}

ENV USER admin
RUN useradd -m $USER -s /bin/bash -G sudo && echo "$USER:$USER" | chpasswd
