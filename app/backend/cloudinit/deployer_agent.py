import subprocess
from flask import Flask, request,jsonify
import json
from pathlib import Path
import requests

app = Flask(__name__)



@app.route("/create")
def create():
    data=json.load(request.data())
    if (not Path.is_file(f"/var/lib/rancher/k3s/server/manifests/shared/{data["nom"]}")):
        subprocess.run(["touch",f"/var/lib/rancher/k3s/server/manifests/shared/{data["nom"]}"])
        subprocess.run(["echo",f"{data["manifest"]} > /var/lib/rancher/k3s/server/manifests/shared/{data["nom"]}"])
    return 200
@app.route("/delete")
def delete():
    data=json.load(request.data())
    subprocess.run(["rm", f"/var/lib/rancher/k3s/server/manifests/shared/{data["nom"]}"])
    return 200
@app.route("/update")
def update():
    data=json.load(request.data())
    if (Path.is_file(f"/var/lib/rancher/k3s/server/manifests/shared/{data["nom"]}")):
        subprocess.run(["echo",f"{data["manifest"]} > /var/lib/rancher/k3s/server/manifests/shared/{data["nom"]}"])
    return 200

app.run(host="0.0.0.0", port=5001)