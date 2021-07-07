from Crypto.Cipher import AES
from PIL import Image


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
    cipher = AES.new(bytearray.fromhex(aes_key), AES.MODE_CBC, bytearray.fromhex(iv))
    encrypted_image = cipher.encrypt(pad(plaintext))[:len(plaintext)]
    print("typeof encrypted",type(encrypted_image))
    return encrypted_image


def decrypt(ciphertext,name,mode,size, aes_key, iv):
    print("decrypted aes_key")
    print(aes_key)
    print("iv-decrypt",iv)
    decrypter = AES.new(bytearray.fromhex(aes_key), AES.MODE_CBC, bytearray.fromhex(iv))
    decrypted_image = decrypter.decrypt(ciphertext)[:len(ciphertext)]
    decrypted = convert_to_RGB(decrypted_image)
    size=size.split()
    size=(int(size[0]),int(size[1]))
    decryptedImage = Image.new(mode, size)
    decryptedImage.putdata(decrypted)
    decryptedImage.save(str(name) + ".png", "PNG")
    return decrypted_image
