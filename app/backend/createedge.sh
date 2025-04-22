#!/bin/bash
 sudo virt-install --name $1 --os-variant ubuntu20.04 --vcpus 2 --ram $2 --location http://ftp.ubuntu.com/ubuntu/dists/focal/main/installer-amd64/ --network bridge=virbr10,model=virtio --graphics none --disk path=/mnt/vms/$1.qcow2,size=20,bus=virtio,format=qcow2 --console pty,target_type=serial --extra-args='auto=true priority=critical console=ttyS0,115200n8 serial'
