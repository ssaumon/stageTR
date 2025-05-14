import subprocess
from flask import Flask, request,jsonify
import requests

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"bonjour":"hello"})