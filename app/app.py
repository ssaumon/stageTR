from flask import Flask, render_template, request
from pathlib import Path
import subprocess

app = Flask(__name__)


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
    print(Path.cwd())
    print(data)
    if "nom" in data.keys() and "ram" in data.keys():
        subprocess.run(["./backend/createedge.sh", data["nom"], data["ram"]])

    
    return render_template("index.j2")

app.run(host="0.0.0.0", port=80)
