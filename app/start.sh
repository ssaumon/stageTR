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

echo installation de mysql
apt install -y mysql-server

echo installation de requirements.txt
pip install --no-cache-dir -r frontend/requirements.txt

echo installation des dépendances fait !

virsh net-define backend/net.xml
virsh net-start virtnet

echo création du commutateur virtuel

chmod +x backend/createedge.sh
chmod +x backend/createiot.sh
chmod +x backend/deleteVM.sh
chmod +x backend/ipvm.sh

echo création de la base de données
chmod +x backend/sql.sh
./backend/sql.sh

if [ -f "/home/jammy-server-cloudimg-amd64.img" ]; then
    echo image déjà installée
else
    echo "installation de l'image"
    wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img
    cp jammy-server-cloudimg-amd64.img /home/
fi

BACKIP=127.0.0.1
export BACKIP=127.0.0.1

python3 frontend/app.py 
