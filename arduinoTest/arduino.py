# check https://flask-socketio.readthedocs.io/en/latest/
# and https://github.com/timmyreilly/Demo-Flask-SocketIO
# Arduino with CH340 on board was used!

from flask import Flask
from flask import render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from models import *
from helpers import *
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# to read from Arduino serial port
import serial
import serial.tools.list_ports  # connect Arduino and get list of ports to check if Arduino connected

# to plot Arduino data in real time
from flask_socketio import SocketIO, emit
import time
import datetime

# for background parallel serial port reading
from threading import Thread
from gevent import monkey
monkey.patch_all()

# configure application
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "secret!"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "sensor.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

socketio = SocketIO(app)
db = SQLAlchemy(app)

status = True
# try to connect Arduino

# get list of all available ports
ports = list(serial.tools.list_ports.comports())
for p in ports:
    port = str(p)[:-16]  # delete ' - USB2.0-Serial' last chars from the port name string if using macOS. comment out  on PC
    try:
        serial = serial.Serial(port, 9600)
        # serial = serial.Serial('COM4', 9600) # uncomment this line if using PC and put the right COM number
        break
    except serial.serialutil.SerialException:
        if p == ports[-1]:
            status = False
        continue


thread = None


# init background read from serial port and then send data when called
def background_stuff():
    while True:
        # repeat every second
        time.sleep(1)

        # read data from serial port
        data = serial.readline().decode("utf-8")

        # convert string to floats representing humidity and temperature
        # for getting valid string format check dht-11 sketch code
        humid = float(data[:4])  # cast string to float
        tempr = float(data[6:10])  # cast string to float
        now = datetime.datetime.now()

        # write into database
        record = Data(tempr, humid, now)
        db.session.add(record)
        db.session.commit()

        # send data
        socketio.emit("message", data=({"humid": humid, "tempr": tempr}), namespace="/test")


@app.route("/")
def index():
    # check if Arduino is connected
    if not status:
        return render_template("index.html", status=status)

    # start background serial port reading
    global thread
    if thread is None:
        thread = Thread(target=background_stuff)
        thread.start()

    return render_template("index.html")


@app.route("/temperature")
def tempr():
    # query database
    rows = db.session.execute("SELECT temperature, timestamp FROM data"
                              " WHERE timestamp BETWEEN datetime('now', 'localtime', 'start of day')"
                              " AND datetime('now', 'localtime')"
                              " GROUP BY strftime('%i', timestamp), temperature")
    # create data for plot
    temperature = []
    timestamp = []
    key = "temperature"
    for row in rows:
        temperature.append(row[0])
        timestamp.append(row[1][:-7])  # delete last 7 digits from timestamp string

    barchart = bar(timestamp, temperature, key)

    # check if there is data for the given period
    if temperature:
        return render_template("temperature.html", barchart=barchart)
    else:
        return render_template("temperature.html", msg=True)


@app.route("/humidity")
def humid():
    # query database
    rows = db.session.execute("SELECT humidity, timestamp FROM data"
                              " WHERE timestamp BETWEEN datetime('now', 'localtime', 'start of day')"
                              " AND datetime('now', 'localtime')"
                              " GROUP BY strftime('%i', timestamp), humidity")
    # create lists of data for plot
    humidity = []
    timestamp = []
    key = "humidity"
    for row in rows:
        humidity.append(row[0])
        timestamp.append(row[1][:-7])  # delete last 7 digits from timestamp string

    barchart = bar(timestamp, humidity, key)

    # check if there is data for the given period
    if humidity:
        return render_template("humidity.html", barchart=barchart)
    else:
        return render_template("humidity.html", msg=True)


@app.route("/choosetemp")
def choosetemp():

    q = request.args.get("select", "day", type=str)

    rows = db.session.execute("SELECT temperature, timestamp FROM data"
                                  " WHERE timestamp BETWEEN {}"
                                  " AND datetime('now', 'localtime')". format(q))
    # create lists of data for plot
    temperature = []
    timestamp = []
    key = "temperature"
    for row in rows:
        temperature.append(row[0])
        timestamp.append(row[1][:-7])  # delete last 7 digits from timestamp string

    # check if there is data for the given period
    if not temperature:
        return jsonify("<h3>There is no available data!</h3><h3>Choose something else</h3>")

    barchart = bar(timestamp, temperature, key)

    return jsonify(barchart)


@app.route("/choosehumid")
def choosehumid():

    q = request.args.get("select", "day", type=str)

    rows = db.session.execute("SELECT humidity, timestamp FROM data"
                                  " WHERE timestamp BETWEEN {}"
                                  " AND datetime('now', 'localtime')". format(q))
    # create lists of data for plot
    humidity = []
    timestamp = []
    key = "humidity"
    for row in rows:
        humidity.append(row[0])
        timestamp.append(row[1][:-7])  # delete last 7 digits from timestamp string

    # check if there is data for the given period
    if not humidity:
        return jsonify("<h3>There is no available data!</h3><h3>Choose something else</h3>")

    barchart = bar(timestamp, humidity, key)

    return jsonify(barchart)


@socketio.on("message", namespace="/test")
def event(msg):
    emit(msg)


if __name__ == "__main__":
    socketio.run(app)
