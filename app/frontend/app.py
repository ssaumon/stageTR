from flask import Flask, render_template, request, send_file, redirect
from pathlib import Path
import subprocess
import requests
import mysql.connector
import re
import time

cnx=mysql.connector.connect(host='127.0.0.1',user="root",port=3306,database="BDD_VMs",password="bonjour")

cur=cnx.cursor()
app = Flask(__name__)
backip=""

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


def maj_prometheus():
    cur.execute("SELECT nom from edge;")
    vms=cur.fetchall()
    cur.execute("SELECT nom from iot;")
    vms.extend(cur.fetchall())
    vms = [n[0] for n in vms ]
    st=""
    for vm in vms:
        st+=f"'{vm}:9100',"
    st=st[:-1]
    prom=""
    with open("backend/prometheus/template_prom")as f:
        prom=f.readlines()

    with open("/etc/prometheus/prometheus.yml","w")as f:
        for row in prom:
            row = re.sub(r"{{liste}}",rf"{st}",row)
            f.write(row)
    subprocess.Popen(["systemctl", "restart", "prometheus"])

def del_prometheus_instance(instances):
    subprocess.run(["systemctl", "stop", "prometheus"])
    enable=subprocess.Popen(["prometheus", "--web.enable-admin-api"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    for line in enable.stdout:
        if re.search(r"ready to receive web requests",line):
            break

    for instance in instances:
        subprocess.run(["curl", "--silent", "-X", "POST", "-g", 'http://localhost:9090/api/v1/admin/tsdb/delete_series?match[]={instance="'+instance+':9100"}'])
    
    subprocess.run(["curl", "--silent", "-X", "POST", "http://localhost:9090/api/v1/admin/tsdb/clean_tombstones"])
    enable.kill()
    subprocess.run(["systemctl", "start", "prometheus"])




@app.route("/")
def index():
    global backip
    backip =request.host
    return redirect("http://"+backip+":80/edge")

@app.route("/edge")
def edge():
    majetatvm()
    global cur
    global backip
    backip =request.host
    cur.close()
    cnx.cmd_reset_connection()
    cur=cnx.cursor()
    cur.execute("SELECT * from edge;")
    vms=cur.fetchall()
    cur.execute("SELECT * from applications;")
    applis=cur.fetchall()
    cur.execute("SELECT cluster,application from associations;")
    assoc=cur.fetchall()
    
    return render_template("edge.j2",vms=vms, backip=backip, applis=applis, assoc=assoc)

@app.route("/iot")
def iot():
    global backip
    backip =request.host
    majetatvm()
    global cur
    cur.close()
    cnx.cmd_reset_connection()
    cur=cnx.cursor()
    cur.execute("SELECT * from iot;")
    vms=cur.fetchall()
    cur.execute("SELECT nom from edge;")
    clusters=[n[0] for n in cur.fetchall()]
    return render_template("iot.j2",vms=vms, backip=backip, clusters=clusters)

@app.route("/app")
def apps():
    global backip
    backip =request.host
    global cur
    cur.close()
    cnx.cmd_reset_connection()
    cur=cnx.cursor()
    cur.execute("SELECT * from applications;")
    apps=cur.fetchall()
    return render_template("app.j2", apps=apps, backip=backip)



@app.route("/createedge", methods=["POST"])
def create_edge():
    global backip
    backip =request.host
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
        elif re.search(r"[\s\(\)\-\&\@\*\$\|\%\~]",nom):
            err="Il y a un espace ou un caractère spécial (( ) - & @ * $ | % ~) dans : "+nom
        elif int(ram)<2048:
            err="RAM insuffisante : "+ram+" < 2048"
        elif int(cpu)<2:
            err="CPUs insuffisants : "+cpu+" < 2"
        else:
            cur.execute("INSERT INTO edge VALUES (%s, %s,%s,'en création');", (nom,cpu,ram))
            cnx.commit()
            subprocess.Popen(["./backend/createedge.sh", nom, ram, cpu])
    else: 
        err="Il manque des informations"
    cur.execute("SELECT * from edge;")
    vms=cur.fetchall()
    maj_prometheus()
    cur.execute("SELECT * from applications;")
    applis=cur.fetchall()
    cur.execute("SELECT cluster,application from associations;")
    assoc=cur.fetchall()
    return render_template("edge.j2",vms=vms, backip=backip, err=err, applis=applis, assoc=assoc)



@app.route("/createiot", methods=["POST"])
def create_iot():
    global backip
    backip =request.host
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
        elif re.search(r"[\s\(\)\-\&\@\*\$\|\%\~]",nom):
            err="Il y a un espace ou un caractère spécial (( ) - & @ * $ | % ~) dans : "+nom
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
    maj_prometheus()
    
    return render_template("iot.j2",vms=vms, backip=backip, clusters=clusters,err=err)



@app.route("/createapp", methods=["POST"])
def create_app():
    global backip
    backip =request.host
    err=None
    data = request.form.to_dict()
    if "nom" in data.keys() and "manifest" in data.keys():
        nom,manifest=data["nom"],data["manifest"]
        cur.execute("SELECT nom from applications;")
        li=[n[0] for n in cur.fetchall()]
        if nom in li:
            err="l'application "+nom+" existe déjà"
        elif re.search(r"[\s\(\)\-\&\@\*\$\|\%\~]",nom):
            err="Il y a un espace ou un caractère spécial (( ) - & @ * $ | % ~) dans : "+nom
        else:
            #r=requests.post(f"{backip}:5000/createapp",data=data)
            man = re.sub('"','\"',manifest)
            cur.execute("INSERT INTO applications VALUES (%s, %s);", (nom,man))
            cnx.commit()
    cur.execute("SELECT * from applications;")
    apps=cur.fetchall()
    return render_template("app.j2", apps=apps, err=err, backip=backip)



@app.route("/delapp", methods=["POST"])
def delapp():
    global backip
    backip =request.host
    data = request.form.to_dict()
    if "nom" in data.keys():
        nom=data["nom"]
        cur.execute("DELETE FROM applications WHERE nom = %s;", (nom,))
        cnx.commit()
        cur.execute("DELETE FROM associations WHERE application = %s;", (nom,))
        cnx.commit()
    cur.execute("SELECT * from applications;")
    apps=cur.fetchall()
    return render_template("app.j2", apps=apps, backip=backip)



@app.route("/deledge", methods=["POST"])
def deledge():
    global backip
    backip =request.host
    data = request.form.to_dict()
    if "nom" in data.keys():
        nom=data["nom"]
        cur.execute("DELETE FROM edge WHERE nom = %s;", (nom,))
        cnx.commit()
        del_prometheus_instance(nom)
        subprocess.run(["./backend/deleteVM.sh", nom])
        cur.execute("DELETE FROM associations WHERE cluster = %s;", (nom,))
        cnx.commit()


        cur.execute("SELECT nom FROM iot WHERE cluster = %s", (nom,))
        iter = [n[0] for n in cur.fetchall()]
        del_prometheus_instance(iter)
        for iot in iter:
            subprocess.run(["./backend/deleteVM.sh", iot])
            cur.execute("DELETE FROM iot WHERE nom = %s;", (iot,))
            cnx.commit()

            

    cur.execute("SELECT * from edge;")
    vms=cur.fetchall()
    maj_prometheus()
    cur.execute("SELECT * from applications;")
    applis=cur.fetchall()
    cur.execute("SELECT cluster,application from associations;")
    assoc=cur.fetchall()

    return render_template("edge.j2", vms=vms, backip=backip, assoc=assoc, applis=applis)



@app.route("/deliot", methods=["POST"])
def deliot():
    global backip
    backip =request.host
    data = request.form.to_dict()
    if "nom" in data.keys():
        nom=data["nom"]
        cur.execute("SELECT cluster FROM iot WHERE nom = %s;",(nom,))
        edge=cur.fetchone()[0]
        requests.get(f"http://{edge}:5001/delnode/{nom}")
        cur.execute("DELETE FROM iot WHERE nom = %s;", (nom,))
        cnx.commit()
        del_prometheus_instance(nom)
        subprocess.Popen(["./backend/deleteVM.sh", nom])
    cur.execute("SELECT * from iot;")
    vms=cur.fetchall()
    cur.execute("SELECT nom from edge;")
    clusters=[n[0] for n in cur.fetchall()]
    maj_prometheus()

    return render_template("iot.j2", vms=vms, backip=backip, clusters=clusters)



@app.route("/modifapp", methods=["POST"])
def modifapp():
    global backip
    backip =request.host
    data = request.form.to_dict()
    print(data)
    if "nom" in data.keys() and "manifest" in data.keys():
        nom,manifest=data["nom"],data["manifest"]
        man = re.sub('"','\"',manifest)
        cur.execute("UPDATE applications SET manifest = %s WHERE nom = %s;", (man,nom))
        cnx.commit()
    cur.execute("SELECT * from applications;")
    apps=cur.fetchall()
    return render_template("app.j2", apps=apps, backip=backip)


@app.route("/affectapp", methods=["POST"])
def affectapp():
    global backip
    backip =request.host
    err=None
    data={}
    data["cluster"] = request.form["cluster"]
    data["applis"]=request.form.getlist('applis')
    data["bouton"] = request.form["bouton"]
    print(data)
    if "cluster" in data.keys() and "applis" in data.keys() and "bouton" in data.keys():
        cur.execute("SELECT * FROM applications")
        selected_applis, applis, cluster, bouton=data["applis"], cur.fetchall(), data["cluster"], data["bouton"]

        liste_invalides=[]
        

        if bouton == "supprimer":
            for appli in selected_applis:
                cur.execute("SELECT cluster, application FROM associations WHERE cluster = %s AND application = %s",(cluster,appli))
                if (cur.fetchone()):
                    if requests.post(f"http://{cluster}:5001/delete",data={"nom":appli}).status_code==200:
                        cur.execute("DELETE FROM associations WHERE cluster = %s AND application = %s;", (cluster,appli))
                        cnx.commit()
                else: liste_invalides.append(appli)
                print(liste_invalides)
            if len(liste_invalides)>0:
                err=""
                for el in liste_invalides:
                    err+=el
                err+=" sont des applications déjà absentes du cluster"

        elif bouton == "ajouter":
            for appli in selected_applis:
                cur.execute("SELECT * FROM applications WHERE nom = %s",(appli,))
                manifest=cur.fetchone()[1]
                cur.execute("SELECT * FROM associations WHERE cluster = %s AND application = %s",(cluster,appli))
                if (not cur.fetchone()) :
                    if requests.post(f"http://{cluster}:5001/create",data={"nom":appli,"manifest":manifest}).status_code==200:
                        man = re.sub('"','\"',manifest)
                        cur.execute("INSERT INTO associations VALUES (%s, %s, %s);", (cluster,appli,man))
                        cnx.commit()
                else: liste_invalides.append(appli)
            print(liste_invalides)
            if len(liste_invalides)>0:
                err=""
                for el in liste_invalides:
                    err+=el
                err+=" sont des applications déjà présentes dans le cluster"


    cur.execute("SELECT * from edge;")
    vms=cur.fetchall()
    cur.execute("SELECT * from applications;")
    applis=cur.fetchall()
    cur.execute("SELECT cluster,application from associations;")
    assoc=cur.fetchall()
    
    return render_template("edge.j2",vms=vms, backip=backip, applis=applis, assoc=assoc, err=err)


@app.route("/details/<vm>", methods=["GET"])
def details(vm):
    global backip
    backip =request.host
    return render_template("details.j2", vm=vm, backip= backip)

@app.route("/Chart.js", methods=["GET"])
def chart():
    return send_file("static/Chart.js")




try:
    app.run(host="0.0.0.0", port=80)
finally:
    cur.close()
    cnx.close()
    print("fin")