#
# Diffie-Hellman Key Exchange
#

from discmath import randprime, primitive_root

def generate_dh_parameters():
    """
    Create a common prime number q and find its primitive root a.
    """
    q = randprime(2**11, 2**16)
    return q, primitive_root(q)

def get_private_key(q):
    """
    Find a random prime within a threshold and less than q, return this as the private key.
    """
    return randprime(2**11, q)

def get_public_key(private_key, q, a):
    """
    Given private_key, shared prime p and primitive root a. Compute the public key.
    """
    return pow(a, private_key, q)

def get_shared_key(public_key, private_key, q):
    """
    Given public_key, private_key and shared prime p, compute shared key K.
    """
    return pow(public_key, private_key, q)
