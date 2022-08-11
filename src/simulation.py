#
# Simulate key exchange with diffie-hellman, using CSPRNG Blum Blum Shub to create a secure communication environment!
#

from bbs import blum_blum_shub, test_csprng
from dh import generate_dh_parameters, get_private_key, get_public_key, get_shared_key
from sdes import encrypt_sdes, decrypt_sdes
import re
import time

def preprocess_file(txt):
    txt = txt.strip()
    txt = txt.replace('\r', '').replace('\t', ' ').replace('\n', ' ') # Remove symbols, msg is a single line.
    return re.sub('\s\s+', ' ', txt) # Remove consecutive whitespace.

def fetch_file(file):
    file = file.replace('\\', '/')
    try:
        with open(file, 'r') as f:
            return preprocess_file(f.read())
    except: # Not a file, or does not exist.
        return file

if __name__ == "__main__":
    q, a = generate_dh_parameters()
    
    A_KEY_PRIV = get_private_key(q) # Alice's priv. key
    A_KEY_PUB = get_public_key(A_KEY_PRIV, q, a) # Alice's pub. key

    B_KEY_PRIV = get_private_key(q) # Bob's priv. key
    B_KEY_PUB = get_public_key(B_KEY_PRIV, q, a) # Bob's pub. key

    SHARED_KEY_1 = get_shared_key(B_KEY_PUB, A_KEY_PRIV, q)
    SHARED_KEY_2 = get_shared_key(A_KEY_PUB, B_KEY_PRIV, q)

    assert SHARED_KEY_1 == SHARED_KEY_2

    SECRET_KEY = blum_blum_shub(10, SHARED_KEY_1) # Passed previous assert = key 1 and key 2 is equivalent.

    print('\nDiffie-Hellman Key Exchange Info: q={}, a={}. Generated random 11-bit to 16-bit primes.'.format(q,a))
    print('Alice\'s private key {}, public key {}.'.format(A_KEY_PRIV, A_KEY_PUB))
    print('Bob\'s private key {}, public key {}.'.format(B_KEY_PRIV, B_KEY_PUB))
    print('Shared Key, {}={}.'.format(SHARED_KEY_1, SHARED_KEY_2))
    print('Secret Encr/Decr Key, 10-bit for S-DES,', SECRET_KEY)
    print('')

    print("Sending public key from Alice to Bob")
    time.sleep(0.150)

    print("Sending public key from Bob to Alice")
    time.sleep(0.150)

    print('\nSend Data:\n')

    message_to_bob = fetch_file(input('Select file path or text to send from Alice: '))
    message_to_alice = fetch_file(input('Select file path or text to send from Bob: '))
    print('')
    
    message_to_bob_encr = encrypt_sdes(message_to_bob, SECRET_KEY)
    message_to_alice_encr = encrypt_sdes(message_to_alice, SECRET_KEY)

    print('Alice is sending to Bob:', message_to_bob, '\nEncrypted:', message_to_bob_encr)
    time.sleep(0.2)
    print('Bob received message from Alice, decrypt with secret key:\n{}'.format(decrypt_sdes(message_to_bob_encr, SECRET_KEY)))
    time.sleep(0.1)

    print('')
    print('Bob is sending to Alice:', message_to_alice, '\nEncrypted:', message_to_alice_encr)
    time.sleep(0.2)
    print('Alice received message from Bob, decrypt with secret key:\n{}'.format(decrypt_sdes(message_to_alice_encr, SECRET_KEY)))
    time.sleep(0.1)

    print('\nCommunication Terminated...')
    