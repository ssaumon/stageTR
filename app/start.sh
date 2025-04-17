apt update
apt install -y python3-pip
apt install -y qemu-kvm libvirt-bin virtinst virt-viewer libguestfs-tools virt-manager uuid-runtime
pip install --no-cache-dir -r requirements.txt

echo installation des dépendances fait !

virsh define backend/net.xml

echo création du commutateur virtuel

chmod +x backend/createedge.sh
python3 app.py
