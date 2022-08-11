# Simple Secure Client/Server Chat

- Run src/chat_server.py to start the server, it utilizes Diffie-Hellman for key exchange, and Simplified DES for symmetric encryption (this can be replaced by DES or AES, etc!).
- Run src/chat_client.py to create a new chat client, the server will share every client's public key with each other, for now you may only talk one-to-one, but this can easily be extended!
- Press CTRL-C to shutdown the server or client(s).

# Prerequisites

- NumPy, pip install numpy
- SymPy, conda install -c anaconda sympy
