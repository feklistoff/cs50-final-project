# CS50x Final Project 2016/2017
Arduino Uno + DHT-11 sensor simple web app
## What's Inside
A simple web application I made for CS50x final project.
It takes Arduino Uno chinese clone (with CH340 chip on board) and DHT-11 temperature/humidity sensor.
Application connects Arduino to python Flask app and sqlite3 database.
There are two main functions of the app: 1 - plot real-time data using charts.js when Arduino is connected;
2 - plot bar chart using plotly library and jquery asynchronous requests for visualization data stored in sqlite db.
## What I Have Done
0. used simple edit for DHT-11 Arduino sketch.
1. pyserial library to connect Arduino and read data from it.
2. for streaming data I've used python threading and flask-socketio.
3. plotting real-time data with chart.js javascript tool.
4. sqlite3 and flask-sqlalchemy for storing data.
5. plotly offline tools for plotting bar chart using stored data.
6. ajax/jquery asynchronous requests for plotting different time-period statistics.
## btw
If you like some of my solutions feel free to use them!
