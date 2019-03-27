#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

documents = {
    'aaa': 'aaaa1',
    'bbb': 'bbbb2'
}


@app.route('/')
def index():
    return "hello"


import ptvsd
ptvsd.enable_attach(address=('0.0.0.0',5678))


@socketio.on('connect')
def test_connect(**args):
    print('wait for attatch')
    ptvsd.wait_for_attach()
    print('attatched')
    previousId = {}
    emit('documents', list(documents.keys()))
    print(f'Socket {socketio.server} has connected')


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=4444)
