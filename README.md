## Metallize
Generate bootable disk images from Dockerfiles.

### Problem

*I want to be able to robustly generate OS images with minimum headache.*

1) Operating system image generation is usually done by taking some vendor boot image, booting it, then applying some automation to it(kickstart, ansible) and freezing into some sort of golden image.

2) Alternatively there are custom solutions like [Yocto](https://www.yoctoproject.org/software-overview/) which constitute a wholy custom solution.

The problem with (1) solution is that it's analogous to `docker commit` workflow, eg nobody uses it in docker world. Yocto-style solutions (2) require learning a whole new ecosystem, that's too much commitment.

### Lets Just Use Docker

OS images are a custom filesystem + init system + bootloader that are converted into a disk image.

Metallize project is a design pattern where 

1) We use docker to generate the filesystem just as we would for any container use-case.
2) Use another docker image to convert that filesystem into a binary bootable image. The bootable image could be a container-like squashfs/overlayfs livecd where every change is reset on restart or a conventional mutable ext4 filesystem.


