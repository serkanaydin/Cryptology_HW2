import hashlib
import os
import socket
import pickle

from Crypto import Random
from PIL import Image
import utils.rsa as RSA
import utils.AES as AES

SERVER_HOST = 'localhost'
SERVER_PORT = 8080
SERVER_PUBLIC_KEY = []

username = ""
user_public_key = []
user_private_key = []

server_public_key = [205, 101]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))


def recv():
    message = pickle.loads(client_socket.recv(4096))
    return message


def send(message):
    client_socket.send(pickle.dumps(message))
    print("Message is sent")


def image_encrpytion(path):
    image = Image.open(path)
    data = image.convert("RGB").tobytes()
    iv = Random.new().read(int(8))
    aes_key = Random.new().read(int(32))
    encrypted_image = AES.encrypt(data, aes_key, iv)
    return encrypted_image, aes_key, iv


def login(username):
    message = {
        "type": "LOGIN",
        "data": {
            "username": username
        }
    }
    send(message)


def register():
    message = {
        "type": "REGISTER",
        "data": {
            "username": username,
            "public_key": user_public_key,
        }
    }
    send(message)


def upload(path):
    image_name = os.path.basename(path)
    encrypted_image, aes_key, iv = image_encrpytion(path)
    digest = hashlib.sha256(encrypted_image)
    private_key_encrypted_digest = RSA.encrypt(str(digest), user_private_key)
    public_key_encrypted_aes_iv = RSA.encrypt("{aes_key} {iv}".format(aes_key=aes_key, iv=iv), server_public_key)

    upload_image_message = {
        "type": "UPLOAD_IMAGE",
        "data": {
            "username": username,
            "image_name": image_name,
            "encrypted_image": encrypted_image,
            "private_key_encrypted_digest": private_key_encrypted_digest,
            "public_key_encrypted_aes_iv": public_key_encrypted_aes_iv
        }
    }
    send(upload_image_message)


def download():
    pass


def console_application():
    print("For help enter -h: ")
    while True:
        option = input().split()

        if option[0] == "-h":
            print("-l => login\n"
                  "-r => register\n"
                  "-u => upload\n"
                  "-d => download\n")

        if option[0] == "-l":
            if option[1] == "-username":
                login(option[2])
        elif option[0] == "-r":
            global username
            if option[1] == "-username":
                username = option[2]
                register()
        elif option[0] == "-u":
            path = option[1]
            upload(path)
        elif option[0] == "-d":
            download()


def main():
    global user_public_key
    global user_private_key
    user_public_key, user_private_key = RSA.rsa_key_generation()
    console_application()


main()
