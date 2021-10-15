
squashfs:
	DOCKER_BUILDKIT=1 docker build --build-arg "SRC_IMG=ubuntu:20.04" -t my-ubuntu -f docker/dummy.dockerfile . --output type=tar,dest=/tmp/src.tar

squashfs-and-syslinux.image:
	DOCKER_BUILDKIT=1 docker build -t $@ -f docker/squashfs-and-syslinux.dockerfile .