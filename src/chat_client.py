#
# Secure Chat Client
#

import sys
import time
import signal
import socket
from threading import Thread
from bbs import blum_blum_shub, test_csprng
from dh import generate_dh_parameters, get_private_key, get_public_key, get_shared_key
from sdes import encrypt_sdes, decrypt_sdes

COMMAND_CONNECT = 1
COMMAND_DISCONNECT = 2
COMMAND_MESSAGE = 3
BUFFER = 2048

SOCKET = None
THREAD_RECEIVE = None
THREAD_QUIT = False
KEYS = {}
PARAMS = None
PUBLIC_KEY = None
PRIVATE_KEY = None

def terminate():
    global SOCKET, THREAD_RECEIVE, THREAD_QUIT
    if SOCKET:
        SOCKET.close()
    SOCKET = None
    THREAD_QUIT = True
    if THREAD_RECEIVE:
        THREAD_RECEIVE.join()
    THREAD_RECEIVE = None

def signal_handler(sig, frame):
    terminate()
    sys.exit(0)

def receive():
    """
    Receive data from the server.
    """
    global SOCKET
    try:
        return SOCKET.recv(BUFFER).decode('ascii').split(',')
    except:
        return None

def receive_async():
    time.sleep(0.1)
    global THREAD_QUIT, SOCKET, KEYS, PARAMS
    while not THREAD_QUIT and SOCKET:
        msg = receive()
        if not msg:
            continue        
        try:
            cmd, user = int(msg[0]), str(msg[1]).lower()
            if cmd == COMMAND_DISCONNECT: # A user disconnected, remove from our list.
                if user in KEYS:
                    del KEYS[user]
                print("{} left the chat.".format(user.capitalize()))
            elif cmd == COMMAND_CONNECT: # A user connected, store the public key and nickname for this user.
                for clients in msg[1:]:
                    user, key = clients.split(':')[0].lower(), clients.split(':')[1]
                    KEYS[user] = int(key)
                    print("{} joined the chat.".format(user.capitalize()))
            elif cmd == COMMAND_MESSAGE: # Read message from user, decrypt with shared key. Given that you know the users public key.
                if user in KEYS:
                    q, a = PARAMS
                    shared = get_shared_key(KEYS[user], PRIVATE_KEY, q)
                    secret = blum_blum_shub(10, shared) # Secret key!
                    print("From {} (PUab {}, Kab {}, Secret {}): {}".format(user.capitalize(), KEYS[user], shared, secret, decrypt_sdes(msg[2], secret)))
        except Exception as e:
            print(e)
            THREAD_QUIT = True

if __name__ == "__main__":    
    SOCKET = None
    THREAD_RECEIVE = None
    THREAD_QUIT = False
    KEYS = {}
    PORT = int(sys.argv[1] if len(sys.argv) > 1 else 5000)
    signal.signal(signal.SIGINT, signal_handler)
    print("Started Secure Chat Client")

    NICK = None # Select a nickname
    while (not NICK or len(NICK) == 0):
        NICK = input("Enter your nickname: ").replace('\n', '').strip()

    q, a = 0, 0 # Diffie-Hellman params recv. from server.
    try:
        print("Connecting to localhost:{}".format(PORT))
        SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SOCKET.connect(('localhost', PORT))
        msg = receive() # Retrieve DH parameters from server.
        PARAMS = (int(msg[0]), int(msg[1]))
        q, a = PARAMS
        
        PRIVATE_KEY = get_private_key(q)
        PUBLIC_KEY = get_public_key(PRIVATE_KEY, q, a)
        print("Your public key is,", PUBLIC_KEY, "and your private key is,", PRIVATE_KEY)
        SOCKET.sendall("{},{}".format(NICK, str(PUBLIC_KEY)).encode('ascii'))

        THREAD_RECEIVE = Thread(target = receive_async)
        THREAD_RECEIVE.start()

        print("Welcome! Write exit to exit, to message someone, write <nickname> <message>\n")
        while not THREAD_QUIT:
            txt = input("").replace('\n', '').strip()
            if txt.lower() == "exit":
                break

            if len(txt) == 0 or not ' ' in txt:
                print("Bad message format, try <nick> <message>!")
                continue
                
            msg = txt.split()
            if len(msg) < 2:
                print("Bad message format, try <nick> <message>!")
                continue
            
            send_to_user = str(msg[0].lower())
            msg = " ".join(msg[1:]).replace(',', '')

            if send_to_user in KEYS:                
                shared = get_shared_key(KEYS[send_to_user], PRIVATE_KEY, q)
                secret = blum_blum_shub(10, shared) # Secret key!
                SOCKET.sendall("{},{}".format(send_to_user, encrypt_sdes(msg, secret)).encode('ascii'))
                print("To {} (PUab {}, Kab {}, Secret {}): {}".format(send_to_user.capitalize(), KEYS[send_to_user], shared, secret, msg))
    except Exception as e:
        print(e)
    finally:
        terminate()
        print("Terminated")
