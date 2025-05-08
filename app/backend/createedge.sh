#!/bin/bash
# sudo virt-install --name $1 --cloud-init cloud-init.yml --os-variant ubuntu20.04 --vcpus $3 --ram $2 --location http://ftp.ubuntu.com/ubuntu/dists/focal/main/installer-amd64/ --network bridge=virbr10,model=virtio --graphics none --disk path=/mnt/vms/$1.qcow2,size=20,bus=virtio,format=qcow2 --console pty,target_type=serial --extra-args='auto=true priority=critical console=ttyS0,115200n8 serial'

# sudo virt-install   --name $1   --memory $2   --vcpus $3   --cloud-init user-data=backend/cloudinit/user-data  --disk path=/home/jammy-server-cloudimg-amd64.img,format=raw   --os-type linux   --os-variant detect=on   --import   --network bridge=virbr10  --graphics none

if [ ! -d "backend/cloudinit/user-data.d" ]; then
    mkdir backend/cloudinit/user-data.d
fi


touch backend/cloudinit/user-data.d/$1
cmd="curl -sfL https://get.k3s.io | sh -s - --token $1"
cat --show-tabs backend/cloudinit/user-data | sed "s/{{hostname}}/$1/g" | sed "s/{{k3scmd}}/$cmd/g" > backend/cloudinit/user-data.d/$1


if [ ! -d "backend/cloudinit/meta-data.d" ]; then
    mkdir backend/cloudinit/meta-data.d
fi


touch backend/cloudinit/meta-data.d/$1
cat --show-tabs backend/cloudinit/meta-data | sed "s/{{hostname}}/$1/g" > backend/cloudinit/meta-data.d/$1

sudo virt-install --name $1 --os-type linux --os-variant detect=on --memory $2 --vcpus $3 --network bridge=virbr10 --graphics none --disk path=/mnt/vms/$1.qcow2,size=20,bus=virtio,format=qcow2,backing_store="/home/jammy-server-cloudimg-amd64.img" --cloud-init user-data=backend/cloudinit/user-data.d/$1,meta-data=backend/cloudinit/meta-data.d/$1,network-config=backend/cloudinit/network-config --import --noautoconsole

ip=""
while [ -z $ip ];
do
ip=$(./backend/ipvm.sh $1)
done
echo "$ip $1 " >> /etc/hosts
mysql -u root --password='bonjour' --database=BDD_VMs -e "UPDATE edge SET statut = 'running' WHERE nom = '$1'; COMMIT;"
echo "VM créée"