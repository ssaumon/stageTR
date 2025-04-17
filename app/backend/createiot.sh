#!/bin/bash
 sudo virt-install --name $1 --os-variant ubuntu20.04 --vcpus $3 --ram $2 --location http://ftp.ubuntu.com/ubuntu/dists/focal/main/installer-amd64/ --network bridge=virbr10,model=virtio --graphics none --extra-args='console=ttyS0,115200n8 serial'
