#!/usr/bin/env python3

from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)

p = Populator()

@app.route('/')
def hello_world():
    return render_template('index.html', name=None)

@app.route('/add_login', methods=['GET', 'POST'])
def add_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        data = "{} {}".format(username, password)
        p.populate_login(data)
        return "Data added: {}".format(data)
    else:
        return "Use POST for credentials!"

@app.route('/add_work', methods=['GET', 'POST'])
def add_work():
    if request.method == 'POST':
        data = request.form['user_ids']
        p.populate_work(data)
        return "Data added: {}".format(data)
    else:
        return "Use POST for user IDs!"
