#
# Blum Blum Shub CSPRNG
#

import random
from sympy.ntheory.factor_ import totient # Used for testing.
from collections import Counter
from utils import circular_left_shift
from discmath import randprime, nextprime

def get_prime(seed):
    """
    Return a large prime which is not a factor in seed.
    """
    p = nextprime(seed)
    while (((p % 4) != 3) or ((seed % p) == 0)):
        p = nextprime(p)
    return p

def get_rand_seed():
    """
    Generate a random seed, for testing. V is phi(N)
    """
    p, q = get_prime(randprime(2**7, 2**10)), get_prime(randprime(2**11, 2**14))    
    N = p*q
    V = totient(N)
    S = random.randint(1,(V-1))
    while ((S % p) == 0) or ((S % q) == 0):
        S = random.randint(1,(V-1))
    return S

def test_csprng(N=1000, bits=50):
    """
    Simple test whether or not the algorithm is compliant to the
    CSPRNG requirements. We want 50% 0, 50% 1 in the bitstring!
    N is the amount of iterations/simulations.
    bits is how many bits to generate for each iteration, in the BBS algorithm.
    """
    result = []
    for _ in range(N):
        result.extend(list(blum_blum_shub(bits, get_rand_seed(), False)))
    v = dict(Counter(result))
    tot = v['0'] + v['1']
    return "Test Results:\n0 - {}, {:.04}\n1 - {}, {:.04}".format(v['0'], (v['0']/tot), v['1'], (v['1']/tot))

def blum_blum_shub(num_bits, seed, return_as_dec=True):
    """
    Generate bitstring, given seed. Using the BBS algorithm.
    p and q are large primes, and not factors of the seed.
    """
    p, q = get_prime(seed), get_prime(circular_left_shift(seed, 2, 64))
    N = p*q
    bitstring = []
    X = ((seed**2) % N)
    for _ in range(num_bits):
        X = (X**2) % N
        B = (X % 2)
        bitstring.append(str(B))
    output = "".join(bitstring)
    return (int(output, 2) if return_as_dec else output)

if __name__ == "__main__":
    print("Testing Blum Blum Shub randomness\n")
    print(test_csprng(500)) # Verify BBS true randomness!
