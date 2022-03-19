# Metallize
Generate bootable disk images from Dockerfiles.

## Problem

If you don't know what an OS image is, you probably don't need this tool, can stop reading now.

>I want to be able to robustly generate OS images with minimum headache.

In particular, I'd like to control exactly what software goes into the image and how the image behaves, eg overlayfs livecd vs mutable ext4. I'd like to be able to target high-performance $100K bare-metal servers, $30 raspberry PIs, $5 cloud VMs and everything inbetween with same tooling. My approach is inspired by how much less painful embedded development is with [esphome](https://esphome.io/).

> For example at home, if I want to deploy a simple raspberry-pi temp logger, I get to define the high-level app in a pleasant dockerfile and then perform a crapton of work in order to deploy that image to a robust bare-metal Linux install. 

> I hit the same problem (the tooling hasn't improved much since dawn of Linux) at work at [Pure Storage](https://www.purestorage.com/) when wanting to quickly evolve a high-performance server image(custom kernel, custom nic tuning, custom networking) and deploy it on 10-20 servers.

Existing approaches suck:

1) Operating system image generation is usually done by taking some vendor boot image, booting it, then applying some automation to it (kickstart, ansible, vargant) and freezing into some sort of golden image. The problem is that this is not cleanly reproducible/automateable. Eg nobody uses `docker commit` it in the container world.

2) Alternatively there are custom solutions like [Yocto](https://www.yoctoproject.org/software-overview/) which constitute a wholy custom solution. This requires learning a whole new ecosystem, including a new distribution, that's too much.

> Idea Behind Metallize: Docker is a common existing skill, lets augment it with bare metal bits

## Quickstart

Install modern docker.

    wget -qO- https://get.docker.com/ | sh

Setup python env:

    python3 -m virtualenv .venv
    ./.venv/bin/python3 -m pip install -r requirements.txt

Generate an ubuntu-based livecd image:
    
    ./.venv/bin/python3 metallize.py profiles/ubuntu20-livecd.iso.yaml |sh

> Note that if you don't pipe to sh, you can preview the commands that will run. This is also handy for debugging metallize.

Now you have a livecd image in `build/livecd.iso`

You can now upload that image into the cloud, burn it onto a cd, write it to usb stick and boot.

Alternatively you can test it with KVM: 

    ./scripts/uefi-boot.sh build/livecd.iso


## Metallize architecture: profile yaml

You can inspect profiles/[ubuntu20-livecd.iso.yaml](profiles/ubuntu20-livecd.iso.yaml) to see how this works. 

The yaml defines a list of docker files which have a parameterized FROM section. You can stack:
* base image(ubuntu:20.04)
* networking choice([ubuntu-netplan.dockerfile](docker/ubuntu-netplan.dockerfile))
* login info([admin-user.dockerfile](docker/admin-user.dockerfile))
* etc

The yaml also defines a `generator` which is another dockerfile like [livecd-generator.dockerfile](docker/livecd-generator.dockerfile).


## Metallize mechanics: profile yaml
The build process looks like:

1) [metallize.py](metallize.py) converts the yaml build profile definition into a sequence (of mostly docker) commands. One usually pipes that into `bash`.
2) Most of the image is build using a sequence of docker build steps, the final steps instead of outputting the image, outputs a tar file. 
3) There are some complications in producing above tar file without a problematic replacing `/etc/resolv.conf`.
4) The tar file is then *passed* into a docker file that knows how to build a particular filesystem, setup bootloaders, etc.

