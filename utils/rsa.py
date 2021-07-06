import random
import numpy as np

def primesInRange(x, y):
    prime_list = []
    for n in range(x, y):
        isPrime = True

        for num in range(2, n):
            if n % num == 0:
                isPrime = False

        if isPrime:
            prime_list.append(n)
    return prime_list


def computeGCD(x, y):
    while y:
        x, y = y, x % y
    return x


def modInverse(e, z):
    for x in range(1, z):
        if ((e % z) * (x % z)) % z == 1:
            return x
    return -1

def generate_key(size):
    key: str = (hex(random.getrandbits(size)))[2:]  # 256 bit key generation,encryption and decryption
    return key


def relativelyPrimesInRange(z):
    prime_list = []
    for n in range(2, z):
        isPrime = True
        if computeGCD(n, z) != 1:
            isPrime = False
        if isPrime:
            prime_list.append(n)
    return prime_list


def rsa_key_generation():
    p = random.choice(primesInRange(3, 50))
    q = random.choice(primesInRange(3, 50))
    while p == q or p * q > 255:
        q = random.choice(primesInRange(3, 50))
    n = p * q
    z = (p - 1) * (q - 1)
    e = random.choice(relativelyPrimesInRange(z))
    d = modInverse(e, z)
    public_key = [n, e]
    private_key = [n, d]
    return public_key, private_key

def encrypt_int(plaintext, public_key):
    encryptedList = []
    for num in plaintext:
        encryptedList.append(pow(num, int(public_key[1])) % int(public_key[0]))
    return encryptedList


def decrypt_int(ciphertext, private_key):
    decryptedList = []
    for num in ciphertext:
        decryptedList.append(pow(num, int(private_key[1])) % int(private_key[0]))
    return decryptedList


def encrypt(plaintext,key):
    print("encrypted-key",key)
    encryptedList = []
    for byte in plaintext:
        encryptedList.append(pow(int(byte, 16), int(key[1])) % int(key[0]))
    return encryptedList


def decrypt(ciphertext,key):
    print("decrypt-key", key)
    decryptedList = []
    for byte in ciphertext:
        decryptedList.append(hex(pow(byte, int(key[1])) % int(key[0])))
    return decryptedList
#-u C:\Users\serka\Desktop\test.jpg
#-u /home/serkan/Desktop/test.png