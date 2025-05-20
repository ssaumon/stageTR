import subprocess
from flask import Flask, request,jsonify
import json
from pathlib import Path
import requests

app = Flask(__name__)

@app.route("/")
def index():
    return 200

@app.route("/create")
def create():
    data=json.load(request.data)
    nom,manifest = data["nom"],data["manifest"]
    if (not Path.is_file(f"/var/lib/rancher/k3s/server/manifests/shared/{nom}")):
        subprocess.run(["touch",f"/var/lib/rancher/k3s/server/manifests/shared/{nom}"])
        subprocess.run(["echo",f"{manifest} > /var/lib/rancher/k3s/server/manifests/shared/{nom}"])
    return 200
@app.route("/delete")
def delete():
    data=json.load(request.data)
    nom = data["nom"]
    subprocess.run(["rm", f"/var/lib/rancher/k3s/server/manifests/shared/{nom}"])
    return 200
@app.route("/update")
def update():
    data=json.load(request.data)
    nom,manifest = data["nom"],data["manifest"]
    if (Path.is_file(f"/var/lib/rancher/k3s/server/manifests/shared/{nom}")):
        subprocess.run(["echo",f"{manifest} > /var/lib/rancher/k3s/server/manifests/shared/{nom}"])
    

app.run(host="0.0.0.0", port=5001)