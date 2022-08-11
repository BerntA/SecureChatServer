#
# Discrete Math Funcs (number theory utility functions)
#

import random
import math

def sieve(N):
    """
    Sieve of Eratosthenes algorithm, generate many primes, store
    in memory for faster lookup, etc.
    """
    v = [True]*N
    for i in range(2, 1+int(math.sqrt(N)), 1):
        if v[i]:
            for j in range(i**2,N,i):
                v[j] = False
    return [i for i in range(N) if v[i]][2:]

PRIMES = sieve(2**17) # Utilize up to 17 bit primes for now.
PRIMES_SET = set(PRIMES)
PRIMES_N = len(PRIMES)

def is_prime(a):
    """
    Check if number a is a prime or not, O(sqrt(a)).
    Fast, check if a has any factors from 2 to sqrt(a), if not = prime.
    """
    if a == 1:
        return False
    return (sum([((a % i) == 0) for i in range(2, 1+int(math.sqrt(a)))]) == 0)

def nextprime(v):
    """
    Search for the next prime from v.
    """
    v += 1
    while not v in PRIMES_SET:
        v += 1
        if v > PRIMES[PRIMES_N - 1]:
            return PRIMES[(PRIMES_N // 2)]
    return v

def prevprime(v):
    """
    Search for the previous prime from v.
    """
    v -= 1
    while not v in PRIMES_SET:
        v -= 1
    return v

def randprime(a, b):
    """
    Find a random prime within [a,b).
    """
    initial = random.randint(a,b-1)
    min_idx, max_idx = 0, (PRIMES_N-1)
    
    while PRIMES[min_idx] < a:
         min_idx = (min_idx + 1) * 2

    while PRIMES[max_idx] > b:
        max_idx = (max_idx - 1) // 2

    if min_idx >= max_idx:
        min_idx = (max_idx - 1)

    return PRIMES[random.randint(min_idx,max_idx) % PRIMES_N]

def primitive_root(a):
    """
    Find lowest primitive root for prime number a. (primitive root modulo A congruent 1)
    """
    coprimes = {i for i in range(1, a) if math.gcd(i,a) == 1}
    for g in range(1, a):
        if coprimes == {pow(g, powers, a) for powers in range(1, a)}:
            return g # Lowest primitive root which 'generates' 1 to a-1.
    return None # No primitive root.

if __name__ == "__main__":
    q = randprime(2**11, 2**16)
    print("Prime {}, primitive root {}".format(q, primitive_root(q)))
