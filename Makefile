export COMPRESS=lz4
export OPTS="-comp lz4 -b 1024K -always-use-fragments -keep-as-directory -no-recovery -exit-on-error"

/tmp/container.tar:
	DOCKER_BUILDKIT=1 docker build --build-arg "SRC_IMG=ubuntu:20.04" -t my-ubuntu -f docker/dummy.dockerfile . --output type=tar,dest=$@

/tmp/squashfs.squashfs:
	docker run -i -v /tmp:/tmp squashfs-and-syslinux.image  mksquashfs - /tmp/squashfs.squashfs -comp lz4 -b 1024K -always-use-fragments -keep-as-directory -no-recovery -exit-on-error -tar  < /tmp/container.tar

squashfs-and-syslinux.image:
	DOCKER_BUILDKIT=1 docker build -t $@ -f docker/squashfs-and-syslinux.dockerfile .