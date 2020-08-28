# coding: utf-8

import json
import datetime
import time

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route('/pipe')
def pipe():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            # ここに game.py の内容を書く．コマンド入力が欲しいときは message = ws.receive() で入力待ち状態に移行する．
            print("message 受信前")
            message = ws.receive()
            print("message 受信後")
            print(message)
            # ws.send("test message")
    return

if __name__ == "__main__":
    app.debug = True
    host = 'localhost'
    port = 8888

    host_port = (host, port)
    server = WSGIServer(
        host_port,
        app,
        handler_class=WebSocketHandler
    )
    server.serve_forever()