#!/usr/bin/env python3

from flask import Flask
from flask import request
from flask import render_template

from Populator import Populator

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
        p.publish_login(data)
        return "Data added: {}".format(data)
    else:
        return "Use POST for credentials!"

@app.route('/add_work', methods=['GET', 'POST'])
def add_work():
    if request.method == 'POST':
        data = request.form['user_ids']
        data = [x.strip() for x in data.split('\n')]
        for user_id in data:
            message = "{} {}".format(user_id, 0)
            p.publish_work(message)
        return "Data added: {}".format(data)
    else:
        return "Use POST for user IDs!"
