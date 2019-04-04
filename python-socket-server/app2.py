#!/usr/bin/env python

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

import time
from flask import Flask, render_template, request
import socketio

# import ptvsd
# ptvsd.enable_attach(address=('0.0.0.0',5678))

# print('wait for attatch')
# ptvsd.wait_for_attach()
# print('attatched')


sio = socketio.Server(logger=True, async_mode=async_mode)
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
app.config['SECRET_KEY'] = 'secret!'
thread = None

documents = {
    'aaa': {'id':'aaa', 'doc': 'aaaa1'},
    'bbb': {'id':'bbb', 'doc': 'bbbb2'}
}

@app.route('/')
def index():
    return "hello"


@sio.on('connect')
def socket_connect(c_sid, environ, *args):

    previousId: str = None
    print(f'Previous ID is {previousId}')

    def safeJoin(sid: str, currentId: str):
        nonlocal previousId

        print(f'Previous ID is {previousId}')
        if previousId is not None:
            sio.leave_room(sid, previousId)
            print(f'Socket {sid} left room {previousId}')

        sio.enter_room(sid, currentId)
        print(f'Socket {sid} joined room {currentId}')
        previousId = currentId

    print(f'Created safeJoin(). id is {id(safeJoin)}') 

    @sio.on('getDoc')
    def getDoc(sid, docId):
        global documents
        print(f'Running getDoc(). id is {id(getDoc)}') 
        print(f'Id of safeJoin() is {id(safeJoin)}') 
        safeJoin(sid, docId)
        doc = documents.get(docId)
        sio.emit('document', doc,
            namespace='/', room=sid, 
            include_self=True, ignore_queue=False)
    
    print(f'Created getDoc(). id is {id(getDoc)}') 

    @sio.on('addDoc')
    def addDoc(sid, doc):
        global documents
        id = doc['id'] 
        documents[id] = doc
        safeJoin(sid, id)
        sio.emit('documents', list(documents.keys()), 
                namespace='/', include_self=True, ignore_queue=False)
        sio.emit('document', doc, 
                namespace='/', room=sid, 
                include_self=True, ignore_queue=False)

    @sio.on('editDoc')
    def editDoc(sid, doc):
        global documents
        id = doc['id']
        documents[id] = doc
        sio.emit('document', doc, 
            namespace='/', room=id, 
            include_self=True, ignore_queue=False)

    sio.emit('documents', list(documents.keys()),
        namespace='/', room=c_sid,
        include_self=True, ignore_queue=False)
    print(f'Socket {c_sid} has connected')

@sio.on('disconnect')
def socket_disconnect(sid, environ):
    print('Client disconnected', sid)

host = '0.0.0.0'
port = 4444
print(f'starting app on port {port}')


if __name__ == '__main__':
    if sio.async_mode == 'threading':
        # deploy with Werkzeug
        app.run(threaded=True)
    elif sio.async_mode == 'eventlet':
        # deploy with eventlet
        import eventlet
        import eventlet.wsgi
        # eventlet.wsgi.server(eventlet.listen((host, port)), app)
        eventlet.wsgi.server(eventlet.listen(('', port)), app, debug=False)

    elif sio.async_mode == 'gevent_uwsgi':
        print('Start the application through the uwsgi server. Example:')
        print('uwsgi --http :5000 --gevent 1000 --http-websockets --master '
              '--wsgi-file app.py --callable app')
    else:
        print('Unknown async_mode: ' + sio.async_mode)
