#
# Secure Chat Server
#

import sys
import signal
import time
import select
import socket
from sdes import encrypt_sdes, decrypt_sdes
from bbs import blum_blum_shub, test_csprng
from dh import generate_dh_parameters, get_private_key, get_public_key, get_shared_key
from utils import get_as_text

COMMAND_CONNECT = 1
COMMAND_DISCONNECT = 2
COMMAND_MESSAGE = 3
BUFFER = 2048

SOCKET = None
CONNECTIONS = None

def terminate():
    global SOCKET, CONNECTIONS
    if CONNECTIONS:
        for socket in CONNECTIONS:
            socket.close()
        CONNECTIONS.clear()
    SOCKET = None

def signal_handler(sig, frame):
    terminate()
    sys.exit(0)

def broadcast(text, excluded=None):
    if CONNECTIONS is None:
        return None

    text = text.encode('ascii')
    for s in CONNECTIONS:
        if s == SOCKET or s == excluded:
            continue
        try:
            s.sendall(text)
        except:
            s.close()
            CONNECTIONS.remove(s)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    PORT = int(sys.argv[1] if len(sys.argv) > 1 else 5000)
    CONNECTIONS = [] # List of active sockets.
    PUBLIC_KEYS = {} # List of public keys linked to nickname + socket, etc.
    SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    SOCKET.bind(('localhost', PORT))
    SOCKET.listen(10)
    CONNECTIONS.append(SOCKET)
    q,a = generate_dh_parameters() # Diffie-Hellman params for this session.

    print('Starting Secure Chat Server -> localhost:{}.'.format(PORT))
    print('Session uses DH parameters, q={} and a={}.\n'.format(q, a))

    while SOCKET:
        available_sockets, _, _ = select.select(CONNECTIONS, [], []) # Only check sockets that are available. Otherwise the main thread will block and wait forever.
        for socket in available_sockets:
            if socket == SOCKET:
                conn, addr = SOCKET.accept()
                CONNECTIONS.append(conn)
                conn.sendall("{},{}".format(q,a).encode('ascii')) # Send Diffie-Hellman parameters to the client.
                data = conn.recv(BUFFER) # Receive public key from new client, using the parameters we just sent!
                if data:
                    v = data.decode('ascii').lower().split(',')
                    PUBLIC_KEYS[conn] = {'nick': v[0], 'key': v[1]}
                    broadcast("{},{}:{}".format(COMMAND_CONNECT,v[0],v[1]), conn)
                    print("{} has joined the chat!".format(v[0].capitalize()))
                    if len(PUBLIC_KEYS.keys()) > 1: # Send all other clients to this new client.
                        conn.sendall("{},{}".format(COMMAND_CONNECT,",".join(["{}:{}".format(x['nick'], x['key']) for o,x in PUBLIC_KEYS.items() if o != conn])).encode('ascii'))
            else: # Handle messages from other clients.
                try:
                    data = socket.recv(BUFFER)
                    if data:
                        data = data.decode('ascii').split(',') # <to user> <message>
                        if data and len(data) == 2:
                            to_user, from_user, msg = data[0], PUBLIC_KEYS[socket]['nick'], data[1]
                            for o, v in PUBLIC_KEYS.items():
                                if v['nick'] == to_user:
                                    print("From {} to {}, MSG -> '{}'.".format(from_user.capitalize(), to_user.capitalize(), get_as_text(msg)))
                                    o.sendall("{},{},{}".format(COMMAND_MESSAGE,from_user,msg).encode('ascii'))
                                    break
                    else:
                        socket.close()
                        if socket in CONNECTIONS:
                            CONNECTIONS.remove(socket)
                        if socket in PUBLIC_KEYS:
                            del PUBLIC_KEYS[socket]
                except:
                    socket.close()
                    if socket in CONNECTIONS:
                        CONNECTIONS.remove(socket)
                    if socket in PUBLIC_KEYS:
                        print("{} has left the chat!".format(PUBLIC_KEYS[socket]['nick'].capitalize()))
                        broadcast("{},{}".format(COMMAND_DISCONNECT,PUBLIC_KEYS[socket]['nick']))                        
                        del PUBLIC_KEYS[socket]

    terminate()
    print("Terminated")
