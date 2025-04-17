apt update
echo installation de python
apt install -y python3-pip

echo installation de qemu-kvm
apt install -y qemu-kvm 

echo installation de virtinst
apt install -y virtinst 

echo installation de virt-viewer
apt install -y virt-viewer 

echo installation de libguestfs-tools
apt install -y libguestfs-tools 

echo installation de virt-manager
apt install -y virt-manager 

echo installation de uuid-runtime
apt install -y uuid-runtime

echo installation de ansible
apt install -y ansible

echo installation de requirements.txt
pip install --no-cache-dir -r requirements.txt

echo installation des dépendances fait !

virsh net-define backend/net.xml
virsh net-start virtnet

echo création du commutateur virtuel

chmod +x backend/createedge.sh
chmod +x backend/createiot.sh

python3 app.py
