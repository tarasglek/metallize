export COMPRESS=lz4
export OPTS="-comp lz4 -b 1024K -always-use-fragments -keep-as-directory -no-recovery -exit-on-error"
WORKDIR=build
USER=$(shell id -u):$(shell id -g)
ISO_SRC_DIR=$(abspath $(WORKDIR)/iso_src)
KERNEL_DIR=$(WORKDIR)/kernel
ISO_BOOT_DIR=$(ISO_SRC_DIR)/isolinux
STRIP_DIR=--transform='s:.*/::'
LIVE_DIR=$(ISO_SRC_DIR)/live
SQUASHFS_ROOT=$(LIVE_DIR)/rootfs.squashfs

build:
	mkdir -p $@

$(WORKDIR)/container.tar: docker/ubuntu-livecd.dockerfile build
	DOCKER_BUILDKIT=1 docker build --build-arg "SRC_IMG=ubuntu:20.04" -t my-ubuntu -f $< .
	# ridiculous dance to get rid of /etc/resolv.conf that leaks from docker
	DOCKER_BUILDKIT=1 docker build --build-arg "SRC_IMG=ubuntu:20.04" -t my-ubuntu -f $< . --output type=tar,dest=- | tar --delete etc/resolv.conf  > $@
	cd build && mkdir -p etc && ln -sf /run/systemd/resolve/resolv.conf etc/resolv.conf
	tar -rvf $@ -C build etc/resolv.conf

$(SQUASHFS_ROOT): $(WORKDIR)/container.tar
	mkdir -p $(LIVE_DIR)
	docker run -i -v $(LIVE_DIR):/tmp --user $(USER) squashfs-and-syslinux.image  mksquashfs - /tmp/$(shell basename $(SQUASHFS_ROOT))  -comp $(COMPRESS) -b 1024K -always-use-fragments -keep-as-directory -no-recovery -exit-on-error -tar  < $<

$(WORKDIR)/livecd.iso: $(WORKDIR)/container.tar squashfs-and-syslinux.image
	mkdir -p $(KERNEL_DIR) $(ISO_SRC_DIR)
	tar --show-transformed-names --transform='s:-.*::' $(STRIP_DIR) -xvf $< -C $(KERNEL_DIR) \
		--wildcards "boot/vmlinuz-*" \
		--wildcards "boot/initrd*-*"
	$(MAKE) $(SQUASHFS_ROOT)
	docker run --user $(USER) \
		-v $(abspath $(KERNEL_DIR)):/boot \
		-v $(ISO_SRC_DIR):/iso_src \
		-v $(abspath $(WORKDIR)):/out \
		squashfs-and-syslinux.image /build.sh

squashfs-and-syslinux.image:
	DOCKER_BUILDKIT=1 docker build -t $@ -f docker/squashfs-and-syslinux.dockerfile .

run: $(WORKDIR)/livecd.iso
	# following arguments are handy for testing in console
	kvm -hda $< -netdev user,id=user.0 -device e1000,netdev=user.0,mac=52:54:00:12:34:56 -m 4096  -serial stdio  -nographic -monitor null
