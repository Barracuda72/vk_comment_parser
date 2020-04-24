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
        try:
            username = request.form['username']
            password = request.form['password']
            if (not username):
                raise Exception("Username shouldn't be empty!")
            if (not password):
                raise Exception("Password shouldn't be empty!")
            data = "{} {}".format(username, password)
            p.publish_login(data)
            return "Data added: {}".format(data)
        except Exception as e:
            return "Error processing request: {}".format(e)
    else:
        return "Use POST for credentials!"

@app.route('/add_work', methods=['GET', 'POST'])
def add_work():
    if request.method == 'POST':
        data = request.form['user_ids']
        data = [x.strip() for x in data.split('\n')]
        errors = []
        for user_id in data:
            try:
                user_id = int(user_id)
            except Exception as e:
                errors.append("Error processing UID '{}': {}".format(user_id, e))
            message = "{} {}".format(user_id, 0)
            p.publish_work(message)
        if (len(errors) == 0):
            return "Data added: {}".format(data)
        else:
            return "There were errors processing your request: <br/>{}".format("<br/>".join(errors))
    else:
        return "Use POST for user IDs!"
