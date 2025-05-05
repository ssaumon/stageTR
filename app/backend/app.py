from flask import Flask, render_template, request
from pathlib import Path
import subprocess

app = Flask(__name__)

@app.route("/createedge", methods=["POST"])
def create_edge():
    data = request.data.to_dict()
    if "nom" in data.keys() and "ram" in data.keys() and "cpu" in data.keys():
        subprocess.Popen(["./createedge.sh", data["nom"], data["ram"], data["cpu"]])
    return

@app.route("/createiot", methods=["POST"])
def create_iot():
    data = request.data.to_dict()
    if "nom" in data.keys() and "ram" in data.keys() and "cpu" in data.keys():
        subprocess.Popen(["./createiot.sh", data["nom"], data["ram"], data["cpu"]])
    return render_template("index.j2")

app.run(host="0.0.0.0", port=5000)