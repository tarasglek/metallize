squashfs-and-syslinux.image:
	DOCKER_BUILDKIT=1 docker build -t $@ -f docker/squashfs-and-syslinux.dockerfile .