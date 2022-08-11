#
# Simple DES implementation
#

import numpy as np

MASK_BIT_0 = 0x000
MASK_BIT_1 = 0x001
MASK_BIT_2 = 0x002
MASK_BIT_3 = 0x004
MASK_BIT_4 = 0x008
MASK_BIT_5 = 0x010
MASK_BIT_6 = 0x020
MASK_BIT_7 = 0x040
MASK_BIT_8 = 0x080
MASK_BIT_9 = 0x100
MASK_BIT_10 = 0x200
MASK_BIT_ALL_2 = 0x003
MASK_BIT_ALL_5 = 0x001F
MASK_BIT_ALL_8 = 0x0FF
MASK_BIT_ALL_10 = 0x3FF

S0 = np.array([
    [1,0,3,2],
    [3,2,1,0],
    [0,2,1,3],
    [3,1,3,2]
], dtype=np.uint8)

S1 = np.array([
    [0,1,2,3],
    [2,0,1,3],
    [3,0,1,0],
    [2,1,0,3]
], dtype=np.uint8)

def circular_left_shift(n, shift, mask, num_bits = 8):
    """
    Do a left circular shift on the number n, keep the bits defined in the mask.
    If we do it on a 5 bit integer, only keep the 5 bits after shifting!
    """
    return (((n << shift)) | (n >> (num_bits - shift))) & mask

def get_subkey(key):
    """
    Create the necessary subkeys.
    """
    permuted_value = (
        ((MASK_BIT_10 & key) >> 6) |
        ((MASK_BIT_9 & key) >> 1) |
        ((MASK_BIT_8 & key) << 2) |
        ((MASK_BIT_7 & key) >> 1) |
        ((MASK_BIT_6 & key) << 3) |
        ((MASK_BIT_5 & key) >> 4) |
        ((MASK_BIT_4 & key) << 3) |
        ((MASK_BIT_3 & key) >> 1) |
        ((MASK_BIT_2 & key) << 1) |
        ((MASK_BIT_1 & key) << 4)
    )

    permuted_value = (circular_left_shift((permuted_value & 0x3E0), 1, 0x3E0, 5) | circular_left_shift((permuted_value & 0x1F), 1, 0x1F, 5))
    key1 = (
        ((MASK_BIT_1 & permuted_value) << 1) |
        ((MASK_BIT_2 & permuted_value) >> 1) |
        ((MASK_BIT_3 & permuted_value) << 1) |
        ((MASK_BIT_4 & permuted_value) << 2) |
        ((MASK_BIT_5 & permuted_value) << 3) |
        ((MASK_BIT_6 & permuted_value) >> 3) |
        ((MASK_BIT_7 & permuted_value) >> 2) |
        ((MASK_BIT_8 & permuted_value) >> 1)
    )

    permuted_value = (circular_left_shift((permuted_value & 0x3E0), 2, 0x3E0, 5) | circular_left_shift((permuted_value & 0x1F), 2, 0x1F, 5))
    key2 = (
        ((MASK_BIT_1 & permuted_value) << 1) |
        ((MASK_BIT_2 & permuted_value) >> 1) |
        ((MASK_BIT_3 & permuted_value) << 1) |
        ((MASK_BIT_4 & permuted_value) << 2) |
        ((MASK_BIT_5 & permuted_value) << 3) |
        ((MASK_BIT_6 & permuted_value) >> 3) |
        ((MASK_BIT_7 & permuted_value) >> 2) |
        ((MASK_BIT_8 & permuted_value) >> 1)
    )
    
    return key1,key2

def get_ip(v):
    return (
    ((MASK_BIT_8 & v) >> 3) |
    ((MASK_BIT_7 & v) << 1) |
    ((MASK_BIT_6 & v)) |
    ((MASK_BIT_5 & v) >> 1) |
    ((MASK_BIT_4 & v) >> 2) |
    ((MASK_BIT_3 & v) << 4) |
    ((MASK_BIT_2 & v) >> 1) |
    ((MASK_BIT_1 & v) << 2)
    )

def get_inv_ip(v):
    return (
    ((MASK_BIT_8 & v) >> 1) |
    ((MASK_BIT_7 & v) >> 4) |
    ((MASK_BIT_6 & v)) |
    ((MASK_BIT_5 & v) << 3) |
    ((MASK_BIT_4 & v) << 1) |
    ((MASK_BIT_3 & v) >> 2) |
    ((MASK_BIT_2 & v) << 2) |
    ((MASK_BIT_1 & v) << 1)
    )

def FK(v, key):
    right = (v & 0xF)
    left = ((v >> 4) & 0xF)
    res = (left ^ F(right, key))
    return (((res << 4) & 0xF0) | right)

def F(R, subkey):
    right = (((MASK_BIT_4 & R) >> 1) | ((MASK_BIT_3 & R) >> 1) | ((MASK_BIT_2 & R) >> 1) | ((MASK_BIT_1 & R) << 3)) # EP1
    left = (((MASK_BIT_4 & R) >> 3) | ((MASK_BIT_3 & R) << 1) | ((MASK_BIT_2 & R) << 1) | ((MASK_BIT_1 & R) << 1)) # EP2

    right = (right ^ ((subkey >> 4) & 0xF))
    left = (left ^ (subkey & 0xF))

    v1 = (((MASK_BIT_4 & right) >> 2) | (MASK_BIT_1 & right))
    v2 = (((MASK_BIT_3 & right) >> 1) | ((MASK_BIT_2 & right) >> 1))

    v3 = (((MASK_BIT_4 & left) >> 2) | (MASK_BIT_1 & left))
    v4 = (((MASK_BIT_3 & left) >> 1) | ((MASK_BIT_2 & left) >> 1))

    result = ((S0[v1,v2] << 2) | (S1[v3,v4]))
    result = (((MASK_BIT_4 & result) >> 3) | ((MASK_BIT_3 & result) << 1) | ((MASK_BIT_2 & result)) | ((MASK_BIT_1 & result) << 2))

    return result

def SW(v):
    return (((v & 0xF0) >> 4) | (((v & 0xF) << 4)))

def encrypt_sdes(plaintext, key):
    key1, key2 = get_subkey(key)
    return "".join([format(get_inv_ip(FK(SW(FK(get_ip(ord(c)),key1)),key2)), '08b') for c in list(plaintext)])

def decrypt_sdes(ciphertext, key):
    key1, key2 = get_subkey(key)    
    return "".join([chr(get_inv_ip(FK(SW(FK(get_ip(int(ciphertext[i:(i+8)],2)),key2)),key1))) for i in range(0, len(ciphertext), 8)])
