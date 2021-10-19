export COMPRESS=lz4
export OPTS="-comp lz4 -b 1024K -always-use-fragments -keep-as-directory -no-recovery -exit-on-error"
WORKDIR=build
ISODIR=$(WORKDIR)/iso
STRIP_DIR=--transform='s:.*/::'

$(WORKDIR)/container.tar: docker/dummy.dockerfile
	DOCKER_BUILDKIT=1 docker build --build-arg "SRC_IMG=ubuntu:20.04" -t my-ubuntu -f $< .
	DOCKER_BUILDKIT=1 docker build --build-arg "SRC_IMG=ubuntu:20.04" -t my-ubuntu -f $< . --output type=tar,dest=$@

$(WORKDIR)/squashfs.squashfs: $(WORKDIR)/container.tar
	docker run -i -v /tmp:/tmp --user $(shell id -u):$(shell id -g) squashfs-and-syslinux.image  mksquashfs - /tmp/squashfs.squashfs -comp $(COMPRESS) -b 1024K -always-use-fragments -keep-as-directory -no-recovery -exit-on-error -tar  < $<

$(WORKDIR)/livecd.iso: $(WORKDIR)/container.tar
	mkdir -p $(ISODIR)
	tar --show-transformed-names --transform='s:-.*::' $(STRIP_DIR) -xvf $< -C $(ISODIR) \
		--wildcards "boot/vmlinuz-*" \
		--wildcards "boot/initrd*-*"
	docker run squashfs-and-syslinux.image tar -c /usr/lib/ISOLINUX/isolinux.bin /usr/lib/syslinux/modules/bios/ldlinux.c32 | tar -C $(ISODIR) $(STRIP_DIR) --show-transformed-names -xv
	
squashfs-and-syslinux.image:
	DOCKER_BUILDKIT=1 docker build -t $@ -f docker/squashfs-and-syslinux.dockerfile .