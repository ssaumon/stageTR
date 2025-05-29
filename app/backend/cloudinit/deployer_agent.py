import subprocess
from flask import Flask, request,jsonify
import json
from pathlib import Path
import requests

app = Flask(__name__)

@app.route("/")
def index():
    return "valid", 200

@app.route("/create", methods=["POST"])
def create():
    data=request.form.to_dict()
    print(data)
    nom,manifest = data["nom"],data["manifest"]
    if (not Path(f"/var/lib/rancher/k3s/server/manifests/shared/{nom}").is_file()):
        subprocess.run(["touch",f"/var/lib/rancher/k3s/server/manifests/shared/{nom}"])
        with open(f"/var/lib/rancher/k3s/server/manifests/shared/{nom}", 'w') as f:
            f.writelines(manifest)
        subprocess.run(["kubectl","apply","-f",f"/var/lib/rancher/k3s/server/manifests/shared/{nom}"])
    return "valide", 200

@app.route("/delete", methods=["POST"])
def delete():
    data=request.form.to_dict()
    print(data)
    nom = data["nom"]
    subprocess.run(["kubectl","delete","-f",f"/var/lib/rancher/k3s/server/manifests/shared/{nom}"])
    subprocess.run(["rm", f"/var/lib/rancher/k3s/server/manifests/shared/{nom}"])
    return "oui", 200

@app.route("/update", methods=["POST"])
def update():
    data=request.form.to_dict()
    print(data)
    nom,manifest = data["nom"],data["manifest"]
    if (Path.is_file(f"/var/lib/rancher/k3s/server/manifests/shared/{nom}")):
        subprocess.run(["echo",f"{manifest} > /var/lib/rancher/k3s/server/manifests/shared/{nom}"])
    return "oui", 200

@app.route("/delnode/<node>", methods=["GET"])
def delnode(node):
    subprocess.run(["kubectl", "delete", "node", node])
    return "node supprimé", 200

app.run(host="0.0.0.0", port=5001)