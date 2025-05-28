if [ -f "backend/.ssh/id_rsa.pub" ]; then
    echo clé déjà créée
else
    echo "création des clés SSH"
    mkdir backend/.ssh
    ssh-keygen -f backend/.ssh/id_rsa
fi

sudo ./rootinstall.sh