from flask import Flask, render_template, session
from dotenv import load_dotenv, find_dotenv
from os import environ as env
import boats
import loads
import login
import json

app = Flask(__name__)
app.register_blueprint(boats.bp)
app.register_blueprint(loads.ld)
app.register_blueprint(login.lg)

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app.secret_key = env.get("APP_SECRET_KEY")


@app.route('/')
def home():
    return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)