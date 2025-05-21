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
    if (not Path.is_file(f"/var/lib/rancher/k3s/server/manifests/shared/{nom}")):
        subprocess.run(["touch",f"/var/lib/rancher/k3s/server/manifests/shared/{nom}"])
        subprocess.run(["echo",f"{manifest} > /var/lib/rancher/k3s/server/manifests/shared/{nom}"])
    return "valide", 200
@app.route("/delete", methods=["POST"])
def delete():
    data=request.form.to_dict()
    print(data)
    nom = data["nom"]
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

app.run(host="0.0.0.0", port=5001)