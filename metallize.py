"""
metallize.py --from image-in-registry/or-build-locally --kernel-and-init ubuntu-image --network 

general:
    compression: lz4
from: image-in-registry/or-build-locally
boot-env: ubuntu-livecd
network: 
    generator: netplan-dhcp
generate:
    generator: ubuntu-livecd
    output: live.iso
"""