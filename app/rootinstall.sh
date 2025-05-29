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

echo installation de prometheus
apt install -y prometheus

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
chmod +x backend/deliphost.sh
chmod +x backend/affectapp.sh

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

if [ -f "backend/.ssh/id_rsa.pub" ]; then
    echo clé déjà créée
else
    echo "création des clés SSH"
    mkdir backend/.ssh
    ssh-keygen -f backend/.ssh/id_rsa
fi

if [ -f "frontend/static/Chart.js" ]; then
    echo Chart.js déjà installé
else
    echo "installation de Chart.js"
    mkdir frontend/static
    touch frontend/static/Chart.js
    curl https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js > frontend/static/Chart.js
fi


if [ -f "frontend/static/hl.js" ]; then
    echo highlight.js déjà installé
else
    echo "installation de highlight.js"
    mkdir frontend/static
    touch frontend/static/hl.js
    curl https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js > frontend/static/hl.js
fi



python3 frontend/app.py 
