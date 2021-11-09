#!/bin/sh
kvm -netdev user,id=user.0 -device e1000,netdev=user.0 -m 4096  -serial stdio -nographic -monitor null -bios /usr/share/ovmf/OVMF.fd -snapshot -hda $@