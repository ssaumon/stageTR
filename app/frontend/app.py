from flask import Flask, render_template, request
from pathlib import Path
import subprocess
import requests
import mysql.connector

cnx=mysql.connector.connect(host='127.0.0.1',user="root",port=3306,database="BDD_VMs",password="bonjour")
cur=cnx.cursor()
app = Flask(__name__)

backip=subprocess.run(["echo", "$BACKIP"]).stdout

@app.route("/")
def index():
    return render_template("index.j2")

@app.route("/edge")
def edge():
    cur.execute("SELECT * from edge;")
    print(cur.fetchall())
    return render_template("edge.j2",vms=cur.fetchall())

@app.route("/iot")
def iot():
    cur.execute("SELECT * from iot;")
    print(cur.fetchall())
    return render_template("iot.j2")

@app.route("/newapp")
def newapp():
    return render_template("newapp.j2")


@app.route("/createedge", methods=["POST"])
def create_edge():
    data = request.form.to_dict()
    if "nom" in data.keys() and "ram" in data.keys():
        #r=requests.post(f"{backip}:5000/createedge",data=data)
        nom,ram,cpu=data["nom"],data["ram"],data["cpu"]
        cur.execute("INSERT INTO edge VALUES (%s, %s,%s,'en création');", (nom,cpu,ram))
        cnx.commit()
        subprocess.Popen(["./backend/createedge.sh", nom, ram, cpu])
    return render_template("index.j2")


@app.route("/createiot", methods=["POST"])
def create_iot():
    data = request.form.to_dict()
    if "nom" in data.keys() and "ram" in data.keys() and "cpu" in data.keys():
        #r=requests.post(f"{backip}:5000/createiot",data=data)
        subprocess.Popen(["./backend/createiot.sh", data["nom"], data["ram"], data["cpu"]])
    return render_template("index.j2")

@app.route("/deledge", methods=["POST"])
def delvm():
    data = request.form.to_dict()
    if "nom" in data.keys():
        nom=data["nom"]
        cur.execute("DELETE FROM edge WHERE nom==%s;", (nom))
        cnx.commit()
        subprocess.run(["./backend/deleteVM.sh", nom])
    return render_template("newapp.j2")

try:
    app.run(host="0.0.0.0", port=80)
finally:
    cur.close()
    cnx.close()
    print("fin")