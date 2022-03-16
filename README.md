## Metallize
Generate bootable disk images from Dockerfiles.

### Problem

*I want to be able to robustly generate OS images with minimum headache.*

If you don't know what an OS image is, you probably don't need this tool, can stop reading now.


1) Operating system image generation is usually done by taking some vendor boot image, booting it, then applying some automation to it(kickstart, ansible) and freezing into some sort of golden image.

2) Alternatively there are custom solutions like [Yocto](https://www.yoctoproject.org/software-overview/) which constitute a wholy custom solution.

The problem with (1) solution is that it's not-easily-reproducible/automateable. Eg nobody uses `docker commit` it in the container world. Yocto-style solutions (2) require learning a whole new ecosystem, including a new distribution, that's too much.

### Overview: Generate filesystem using docker + add bits to make it bootable
Metallize project is a recipe for building vm images where 

1) We use a series of Dockerfiles to generate the filesystem just as we would for any container use-case.
2) Use another docker image to convert that filesystem into a binary bootable image. The bootable image could be a container-style squashfs/overlayfs livecd where every change is reset on restart or a conventional mutable ext4 filesystem.

### Example

