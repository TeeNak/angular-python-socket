#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

# import ptvsd
# ptvsd.enable_attach(address=('0.0.0.0',5678))

# print('wait for attatch')
# ptvsd.wait_for_attach()
# print('attatched')


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

previousIdBySid = {}

@app.route('/')
def index():
    return "hello"

@socketio.on('connect')
def socket_connect(**args):

    # previousId: str = None
    # print(f'Previous ID is {previousId}')

    def safeJoin(currentId: str):
        previousId = previousIdBySid.get(request.sid)

        print(f'Previous ID is {previousId}')
        if previousId is not None:
            leave_room(previousId)
            print(f'Socket {request.sid} left room {previousId}')

        join_room(currentId)
        print(f'Socket {request.sid} joined room {currentId}')
        previousIdBySid[request.sid] = currentId

    print(f'Created safeJoin(). id is {id(safeJoin)}') 

    @socketio.on('getDoc')
    def getDoc(docId):
        global documents
        print(f'Running getDoc(). id is {id(getDoc)}') 
        print(f'Id of safeJoin() is {id(safeJoin)}') 
        safeJoin(docId)
        doc = documents.get(docId)
        emit('document', doc)
    
    print(f'Created getDoc(). id is {id(getDoc)}') 

    @socketio.on('addDoc')
    def addDoc(doc):
        global documents
        id = doc['id'] 
        documents[id] = doc
        safeJoin(id)
        emit('documents', list(documents.keys()), broadcast=True)
        emit('document', doc)

    @socketio.on('editDoc')
    def editDoc(doc):
        global documents
        id = doc['id']
        documents[id] = doc
        emit('document', doc, room=id)

    emit('documents', list(documents.keys()))
    print(f'Socket {request.sid} has connected')

@socketio.on('disconnect')
def socket_disconnect():
    print('Client disconnected', request.sid)

port = 4444
print(f'starting app on port {port}')

if __name__ == '__main__':
    # socketio.run(app, debug=True, host='0.0.0.0', port=port)
    socketio.run(app, debug=False, use_reloader=False, host='0.0.0.0', port=port) # for ptvsd debug enabled
