apt update
apt install -y python3-pip
pip install --no-cache-dir -r requirements.txt

echo installation des dépendances fait !

python3 app.py
