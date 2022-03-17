# Metallize
Generate bootable disk images from Dockerfiles.

## Problem

If you don't know what an OS image is, you probably don't need this tool, can stop reading now.


*I want to be able to robustly generate OS images with minimum headache.*


In particular, I'd like to control exactly what software goes into the image and how the image behaves, eg overlayfs livecd vs mutable ext4.

Existing approaches suck:

1) Operating system image generation is usually done by taking some vendor boot image, booting it, then applying some automation to it(kickstart, ansible) and freezing into some sort of golden image. The problem is that this is not easily reproducible/automateable. Eg nobody uses `docker commit` it in the container world.

2) Alternatively there are custom solutions like [Yocto](https://www.yoctoproject.org/software-overview/) which constitute a wholy custom solution. This requires learning a whole new ecosystem, including a new distribution, that's too much.

## Idea Behind Metallize: Docker is Great for Generating Filesystems, Shipping Tools

1) We use one or more Dockerfiles to generate the filesystem just as we would for any container use-case.
1) Ensure that fs has kernel + init system + networking configured
2) Pipe that filesystem into a special docker image that knows how to make filesystems

## Quickstart

```
python3 -m virtualenv .venv
./.venv/bin/python3 -m pip install -r requirements.txt
