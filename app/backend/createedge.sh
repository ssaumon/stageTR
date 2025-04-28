#!/bin/bash
# sudo virt-install --name $1 --cloud-init cloud-init.yml --os-variant ubuntu20.04 --vcpus $3 --ram $2 --location http://ftp.ubuntu.com/ubuntu/dists/focal/main/installer-amd64/ --network bridge=virbr10,model=virtio --graphics none --disk path=/mnt/vms/$1.qcow2,size=20,bus=virtio,format=qcow2 --console pty,target_type=serial --extra-args='auto=true priority=critical console=ttyS0,115200n8 serial'

# sudo virt-install   --name $1   --memory $2   --vcpus $3   --cloud-init user-data=backend/cloudinit/user-data  --disk path=/home/jammy-server-cloudimg-amd64.img,format=raw   --os-type linux   --os-variant detect=on   --import   --network bridge=virbr10  --graphics none
touch cloudinit/user-data/$1
cat --show-tabs clondinit/user-data | sed "s/{{hostname}}/$1/g" > cloudinit/user-data/$1

sudo virt-install --name $1 --os-variant detect=on,name=ubuntujammy --memory $2 --vcpus $3 --network bridge=virbr10,model=virtio --graphics none --disk path=/mnt/vms/$1.qcow2,size=20,bus=virtio,format=qcow2,backing_store="/home/jammy-server-cloudimg-amd64.img" --cloud-init user-data=cloudinit/user-data/$1 --import
