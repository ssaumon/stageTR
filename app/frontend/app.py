from flask import Flask, render_template, request
from pathlib import Path
import subprocess
import requests
import mysql.connector
import re

cnx=mysql.connector.connect(host='127.0.0.1',user="root",port=3306,database="BDD_VMs",password="bonjour")

cur=cnx.cursor()
app = Flask(__name__)

backip=subprocess.run(["echo", "$BACKIP"]).stdout

def majetatvm():
    global cur
    cur.close()
    cnx.cmd_reset_connection()
    cur=cnx.cursor()
    cur.execute("SELECT * from edge;")
    vms=cur.fetchall()
    listeVM = subprocess.run(["virsh", "list", "--all"],stdout=subprocess.PIPE,text=True)
    reponse=listeVM.stdout.split("\n")
    etats=[]
    for row in reponse:
        if len(row.split())>1 and row.split()[0]!="Id":
            etats.append(row.split()) 
    print(etats)
    for vm in vms:
        print("oui")


@app.route("/")
def index():
    return render_template("index.j2")

@app.route("/edge")
def edge():
    majetatvm()
    global cur
    cur.close()
    cnx.cmd_reset_connection()
    cur=cnx.cursor()
    cur.execute("SELECT * from edge;")
    vms=cur.fetchall()
    
    return render_template("edge.j2",vms=vms)

@app.route("/iot")
def iot():
    global cur
    cur.close()
    cnx.cmd_reset_connection()
    cur=cnx.cursor()
    cur.execute("SELECT * from iot;")
    vms=cur.fetchall()
    return render_template("iot.j2",vms=vms)

@app.route("/app")
def apps():
    global cur
    cur.close()
    cnx.cmd_reset_connection()
    cur=cnx.cursor()
    cur.execute("SELECT * from applications;")
    apps=cur.fetchall()
    return render_template("app.j2", apps=apps)



@app.route("/createedge", methods=["POST"])
def create_edge():
    err=None
    data = request.form.to_dict()
    if "nom" in data.keys() and "ram" in data.keys():
        #r=requests.post(f"{backip}:5000/createedge",data=data)
        nom,ram,cpu=data["nom"],data["ram"],data["cpu"]
        cur.execute("SELECT nom from iot;")
        li=[n[0] for n in cur.fetchall()]
        cur.execute("SELECT nom from edge;")
        li.extend([n[0] for n in cur.fetchall()])
        print(li)
        if nom in li:
            err="le nom "+nom+" est déjà utilisé"
        elif re.search(r"\s",nom):
            err="Il y a un espace dans : "+nom
        elif int(ram)<2048:
            err="RAM insuffisante : "+ram+" < 2048"
        elif int(cpu)<2:
            err="CPUs insuffisants : "+cpu+" < 2"
        else:
            cur.execute("INSERT INTO edge VALUES (%s, %s,%s,'en création');", (nom,cpu,ram))
            cnx.commit()
            subprocess.Popen(["./backend/createedge.sh", nom, ram, cpu])
        cur.execute("SELECT * from edge;")
        vms=cur.fetchall()
    return render_template("edge.j2",vms=vms, err=err)



@app.route("/createiot", methods=["POST"])
def create_iot():
    err=None
    data = request.form.to_dict()
    if "nom" in data.keys() and "ram" in data.keys() and "cpu" in data.keys():
        nom,ram,cpu=data["nom"],data["ram"],data["cpu"]
        cur.execute("SELECT nom from iot;")
        li=[n[0] for n in cur.fetchall()]
        cur.execute("SELECT nom from edge;")
        li.extend([n[0] for n in cur.fetchall()])
        print(li)
        if nom in li:
            err="le nom "+nom+" est déjà utilisé"
        elif re.search(r"\s",nom):
            err="Il y a un espace dans : "+nom
        elif int(ram)<512:
            err="RAM insuffisante : "+ram+" < 512"
        elif int(cpu)<1:
            err="CPUs insuffisants : "+cpu+" < 1"
        else:
            #r=requests.post(f"{backip}:5000/createiot",data=data)
            
            cur.execute("INSERT INTO iot VALUES (%s, %s,%s,'en création');", (nom,cpu,ram))
            cnx.commit()
            subprocess.Popen(["./backend/createiot.sh", nom, ram, cpu])
    cur.execute("SELECT * from iot;")
    vms=cur.fetchall()
    return render_template("iot.j2",vms=vms, err=err)



@app.route("/createapp", methods=["POST"])
def create_app():
    err=None
    data = request.form.to_dict()
    if "nom" in data.keys() and "manifest" in data.keys():
        nom,manifest=data["nom"],data["manifest"]
        cur.execute("SELECT nom from applications;")
        li=[n[0] for n in cur.fetchall()]
        if nom in li:
            err="l'application "+nom+" existe déjà"
        elif re.search(r"\s",nom):
            err="Il y a un espace dans : "+nom
        else:
            #r=requests.post(f"{backip}:5000/createapp",data=data)
            man = re.sub('"','\"',manifest)
            cur.execute("INSERT INTO applications VALUES (%s, %s);", (nom,man))
            cnx.commit()
    cur.execute("SELECT * from applications;")
    apps=cur.fetchall()
    return render_template("app.j2", apps=apps, err=err)



@app.route("/delapp", methods=["POST"])
def delapp():
    data = request.form.to_dict()
    if "nom" in data.keys():
        nom=data["nom"]
        cur.execute("DELETE FROM applications WHERE nom = %s;", (nom,))
        cnx.commit()
    cur.execute("SELECT * from applications;")
    apps=cur.fetchall()
    return render_template("app.j2", apps=apps)



@app.route("/deledge", methods=["POST"])
def deledge():
    data = request.form.to_dict()
    if "nom" in data.keys():
        nom=data["nom"]
        cur.execute("DELETE FROM edge WHERE nom = %s;", (nom,))
        cnx.commit()
        subprocess.Popen(["./backend/deleteVM.sh", nom])
    cur.execute("SELECT * from edge;")
    vms=cur.fetchall()
    return render_template("edge.j2", vms=vms)



@app.route("/deliot", methods=["POST"])
def deliot():
    data = request.form.to_dict()
    if "nom" in data.keys():
        nom=data["nom"]
        cur.execute("DELETE FROM iot WHERE nom = %s;", (nom,))
        cnx.commit()
        subprocess.Popen(["./backend/deleteVM.sh", nom])
    cur.execute("SELECT * from iot;")
    vms=cur.fetchall()
    return render_template("iot.j2", vms=vms)



@app.route("/modifapp", methods=["POST"])
def modifapp():
    data = request.form.to_dict()
    print(data)
    if "nom" in data.keys() and "manifest" in data.keys():
        nom,manifest=data["nom"],data["manifest"]
        man = re.sub('"','\"',manifest)
        cur.execute("UPDATE applications SET manifest = %s WHERE nom = %s;", (man,nom))
        cnx.commit()
    cur.execute("SELECT * from applications;")
    apps=cur.fetchall()
    return render_template("app.j2", apps=apps)


try:
    app.run(host="0.0.0.0", port=80)
finally:
    cur.close()
    cnx.close()
    print("fin")