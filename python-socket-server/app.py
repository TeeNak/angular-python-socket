#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

import ptvsd
ptvsd.enable_attach(address=('0.0.0.0',5678))


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
    'aaa': {'id':'aaa', 'doc': 'aaaa1'},
    'bbb': {'id':'bbb', 'doc': 'bbbb2'}
}


@app.route('/')
def index():
    return "hello"


print('wait for attatch')
ptvsd.wait_for_attach()
print('attatched')

previousId: str = None

@socketio.on('connect')
def test_connect(**args):
    emit('documents', list(documents.keys()))
    print(f'Socket {socketio.server} has connected')
    print(f'sid {request.sid}')


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)

def safeJoin(currentId: str):
    global previousId
    if previousId is None:
        leave_room(previousId)
    join_room(currentId, lambda _: print(f'Socket {request.sid} joined room {currentId}'))
    previousId = currentId

@socketio.on('getDoc')
def getDoc(docId):
    global documents 
    safeJoin(docId)
    doc = documents.get(docId)
    emit('document', doc)

@socketio.on('addDoc')
def addDoc(doc):
    global documents 
    documents[doc.id] = doc
    safeJoin(doc.id)
    socketio.emit('documents', list(documents.keys()))
    socketio.emit('document', doc)

@socketio.on('editDoc')
def editDoc(doc):
    global documents
    documents[doc.id] = doc
    # socketio.to(doc.id).emit('document', doc)
    socketio.emit('document', doc)






if __name__ == '__main__':
    # socketio.run(app, debug=True, host='0.0.0.0', port=4444)
    # for ptvsd debug
    socketio.run(app, debug=False, use_reloader=False, host='0.0.0.0', port=4444)
