import os
import datetime
import time
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

channels = {"Channel1":[], "Channel2":[], "Channel3":[], "Channel4":[]}
current_channel = "Choose channel"
names = []

# Route to home page
@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html", channels=channels.keys())

# Check if the name is taken
@app.route("/name", methods=["POST"])
def name():
    name = request.form.get("name")
    message_name = ""
    if name in names:
        message_name = "The name {0} already exists.".format(name)
    else:
        message_name = name
        names.append(name)
    return jsonify(message_name)

# Create new channel
@app.route("/channel", methods=["POST"])
def channel():
    new_channel = request.form.get("new_channel")
    message_channel = ""
    if new_channel in channels:
        message_channel = "The channel {0} already exists.".format(new_channel)
    else:
        message_channel = "ok"
    return jsonify(message_channel)

# Announce new channel
@socketio.on("create new channel")
def create_new_channel(data):
    new_channel = data["new_channel"]
    channels[new_channel] = []
    emit("announce new channel", {"new_channel":new_channel} , broadcast=True)


# Load existing posts
@app.route("/posts", methods=["POST"])
def posts():
    current_channel = request.form.get("current_channel")
    data = channels.get(current_channel)
    return jsonify(data)

# Emit new post
@socketio.on("submit post")
def post(data):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    post = data["post"] + " <-- " + st
    on_channel = data["on_channel"]
    if len(channels.get(on_channel)) < 100:
        channels[on_channel].append(post)
    else:
        del channels[on_channel][0]
        channels[on_channel].append(post)
    emit("announce post", {"post": post, "on_channel": on_channel}, broadcast=True)
