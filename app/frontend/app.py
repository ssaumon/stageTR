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
    vmsedge=cur.fetchall()
    cur.execute("SELECT * from iot;")
    vmsiot=cur.fetchall()
    listeVM = subprocess.run(["virsh", "list", "--all"],stdout=subprocess.PIPE,text=True)
    reponse=listeVM.stdout.split("\n")
    etats={}
    for row in reponse:
        r=row.split()
        if len(r)>1 and r[0]!="Id":
            st=""
            for i in range (2,len(r)):
                st+=r[i]+" "
            etats[r[1]]= st
    for vm in vmsedge:
        if vm[3] != "en création":
            cur.execute("UPDATE edge SET statut = %s WHERE nom = %s",(etats[vm[0]],vm[0]))
            cnx.commit()
    for vm in vmsiot:
        if vm[3] != "en création":
            cur.execute("UPDATE iot SET statut = %s WHERE nom = %s",(etats[vm[0]],vm[0]))
            cnx.commit()


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
    cur.execute("SELECT * from applications;")
    applis=cur.fetchall()
    
    return render_template("edge.j2",vms=vms, applis=applis)

@app.route("/iot")
def iot():
    majetatvm()
    global cur
    cur.close()
    cnx.cmd_reset_connection()
    cur=cnx.cursor()
    cur.execute("SELECT * from iot;")
    vms=cur.fetchall()
    cur.execute("SELECT nom from edge;")
    clusters=[n[0] for n in cur.fetchall()]
    return render_template("iot.j2",vms=vms, clusters=clusters)

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
    if "nom" in data.keys() and "ram" in data.keys() and "cpu" in data.keys() and "cluster" in data.keys():
        nom,ram,cpu,cluster=data["nom"],data["ram"],data["cpu"],data["cluster"]
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
            
            cur.execute("INSERT INTO iot VALUES (%s, %s,%s,'en création',%s);", (nom,cpu,ram,cluster))
            cnx.commit()
            subprocess.Popen(["./backend/createiot.sh", nom, ram, cpu, cluster])
    else: 
        err="Il manque des informations"
    cur.execute("SELECT * from iot;")
    vms=cur.fetchall()
    cur.execute("SELECT nom from edge;")
    clusters=[n[0] for n in cur.fetchall()]
    return render_template("iot.j2",vms=vms, clusters=clusters,err=err)



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
        subprocess.run(["./backend/deleteVM.sh", nom])

        cur.execute("SELECT nom FROM iot WHERE cluster = %s", (nom,))
        iter = [n[0] for n in cur.fetchall()]
        for iot in iter:
            subprocess.run(["./backend/deleteVM.sh", iot])
            cur.execute("DELETE FROM iot WHERE nom = %s;", (iot,))
            cnx.commit()

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
    cur.execute("SELECT nom from edge;")
    clusters=[n[0] for n in cur.fetchall()]
    return render_template("iot.j2", vms=vms, clusters=clusters)



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

@app.route("/affectapp", methods=["POST"])
def affectapp():
    data = request.form.to_dict()
    if "cluster" in data.keys() and "applis" in data.keys():
        cur.execute("SELECT * FROM applications")
        cluster,applis=data["cluster"],cur.fetchall()
        for appli in applis:
            if appli[0] in data["applis"]:
                subprocess.run(["touch", f"backend/shared/{cluster}/{appli[0]}"])
                with open(f"backend/shared/{cluster}/{appli[0]}","w")as f:
                    f.write(appli[1])

try:
    app.run(host="0.0.0.0", port=80)
finally:
    cur.close()
    cnx.close()
    print("fin")