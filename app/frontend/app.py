from flask import Flask, render_template, request
from pathlib import Path
import subprocess
import requests
app = Flask(__name__)

backip=subprocess.run(["echo", "$BACKIP"]).stdout

@app.route("/")
def index():
    return render_template("index.j2")

@app.route("/edge")
def edge():
    return render_template("edge.j2")

@app.route("/iot")
def iot():
    return render_template("iot.j2")

@app.route("/newapp")
def newapp():
    return render_template("newapp.j2")

@app.route("/createedge", methods=["POST"])
def create_edge():
    data = request.form.to_dict()
    if "nom" in data.keys() and "ram" in data.keys():
        #r=requests.post(f"{backip}:5000/createedge",data=data)
        subprocess.Popen(["./backend/createedge.sh", data["nom"], data["ram"], data["cpu"]])
    return render_template("index.j2")

@app.route("/createiot", methods=["POST"])
def create_iot():
    data = request.form.to_dict()
    if "nom" in data.keys() and "ram" in data.keys() and "cpu" in data.keys():
        #r=requests.post(f"{backip}:5000/createiot",data=data)
        subprocess.Popen(["./backend/createiot.sh", data["nom"], data["ram"], data["cpu"]])
    return render_template("index.j2")

app.run(host="0.0.0.0", port=80)
