from Crypto.Cipher import AES


def pad(data):  # hexadecimal formatting
    return data + b"\x00" * (16 - len(data) % 16)


def convert_to_RGB(data):
    r, g, b = tuple(map(lambda d: [data[i] for i in range(0, len(data)) if i % 3 == d],
                        [0, 1, 2]))
    pixels = tuple(zip(r, g, b))
    return pixels


def encrypt(plaintext, aes_key, iv):
    print("aes-key")
    print(aes_key)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    encrypted_image = cipher.encrypt(pad(plaintext))[:len(plaintext)]
    return encrypted_image


def decrypt(ciphertext, aes_key, iv):
    decrypter = AES.new(aes_key, AES.MODE_CBC, iv)
    decrypted_image = decrypter.decrypt(ciphertext)[:len(ciphertext)]
    return decrypted_image
