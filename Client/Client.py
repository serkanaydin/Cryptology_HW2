import hashlib
import os
import socket
import pickle

import sys
from pathlib import Path

sys.path.insert(0, "..")
from PIL import Image
import utils.rsa as RSA
import utils.AES as AES

SERVER_HOST = 'localhost'
SERVER_PORT = 8080
SERVER_PUBLIC_KEY = []

username = ""
user_public_key = []
user_private_key = []

server_public_key = [123, 17]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))


def recv():
    data = b''
    l = 4096
    while l == 4096:
        d = client_socket.recv(l)
        l = len(d)
        data += d
    message = pickle.loads(data)
    return message


def send(message):
    client_socket.send(pickle.dumps(message))
    print("Message is sent")


def image_encrpytion(path):
    image = Image.open(path)
    data = image.convert("RGB").tobytes()
    iv = RSA.generate_key(128)
    aes_key = RSA.generate_key(256)
    print("image-encrytion aeskey", aes_key)
    encrypted_image = AES.encrypt(data, aes_key, iv)
    print(image.size, image.mode)
    return encrypted_image, image.mode, image.size, aes_key, iv


def get_client_notifications():
    message = {
        "type": "GET_NOTIFICATIONS",
        "username": username
    }
    send(message)
    message = recv()
    if message["type"] == "NOTIFICATION_LIST":
        notifications = message["notification_list"]
        for uploader, image_name in notifications.items():
            print("Uploader: {uploader} Image name: {image_name}".format(uploader=uploader,
                                                                         image_name=image_name))


def login(name):
    global username
    username = name
    read_keys()
    print("public: ", user_public_key)
    print("private: ", user_private_key)
    message = {
        "type": "LOGIN",
        "data": {
            "username": username
        }
    }
    send(message)


def register():
    generate_keys()
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
    encrypted_image, mode, size, aes_key, iv = image_encrpytion(path)
    size = "" + str(size[0]) + " " + str(size[1])
    digest = hashlib.sha256(encrypted_image).hexdigest().lower()
    print("digest: ", digest)
    print("aes_key-upload", aes_key)
    private_key_encrypted_digest = RSA.encrypt(digest, user_private_key)
    public_key_encrypted_aes = RSA.encrypt(aes_key, server_public_key)
    public_key_encrypted_iv = RSA.encrypt(iv, server_public_key)

    upload_image_message = {
        "type": "UPLOAD_IMAGE",
        "data": {
            "username": username,
            "image_name": image_name,
            "mode": mode,
            "size": size,
            "encrypted_image": encrypted_image,
            "private_key_encrypted_digest": private_key_encrypted_digest,
            "public_key_encrypted_aes": public_key_encrypted_aes,
            "public_key_encrypted_iv": public_key_encrypted_iv
        }
    }

    send(upload_image_message)


def download_request(image_name):
    download_image_message = {
        "type": "DOWNLOAD_IMAGE",
        "data": {
            "username": username,
            "image_name": image_name
        }
    }
    send(download_image_message)


def download_image(message):
    if message["type"] == "IMAGE_RECEIVED":
        image_name = message["data"]["image_name"]
        encrypted_image = message["data"]["encrypted_image"]
        digest = message["data"]["digest"]
        uploader_certificate = message["data"]["certificate"]
        requester_public_key_encrypted_aes = message["data"]["requester_public_key_encrypted_aes"]
        requester_public_key_encrypted_iv = message["data"]["requester_public_key_encrypted_iv"]
        image_mode = message["data"]["mode"]
        image_size = message["data"]["size"]

        uploader_public_key = RSA.decrypt_int(uploader_certificate, server_public_key)
        uploader_public_key = [int(uploader_public_key[0], 16), int(uploader_public_key[1], 16)]
        print("upload_public_key", uploader_public_key)
        digest = RSA.decrypt_int(digest, uploader_public_key)
        incoming_digest = ""
        for hex in digest:
            incoming_digest += str(hex)
        generated_digest = hashlib.sha256(encrypted_image).hexdigest().lower()
        print("id", incoming_digest)
        print("gd", generated_digest)
        if incoming_digest == generated_digest:
            print("Integrity provided")
            aes = RSA.decrypt(requester_public_key_encrypted_aes, user_private_key)
            iv = RSA.decrypt(requester_public_key_encrypted_iv, user_private_key)
            aes_str = ""
            for hex in aes:
                aes_str += str(hex)
            iv_str = ""
            for hex in iv:
                iv_str += str(hex)
            print("before aes decrypt", aes)
            AES.decrypt(encrypted_image, image_name, image_mode, image_size, aes_str, iv_str)


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
            image_name = option[1]
            download_request(image_name)
        elif option[0] == "-c":
            pass

        message = recv()
        if message["type"] == "NOTIFICATION":
            uploader_username = message["data"]["username"]
            image_name = message["data"]["image_name"]
            print(uploader_username + " uploaded image: " + image_name)
            message = {
                "type": "NOTIFICATION_RECEIVED",
                "data": {
                    "received_user": username,
                    "image_name": image_name
                }
            }
            send(message)

        if message["type"] == "IMAGE_RECEIVED":
            download_image(message)

        if message["type"] == "LOGIN SUCCESSFUL":
            get_client_notifications()


def read_keys():
    global user_public_key
    global user_private_key
    f = open(username + ".txt", "r")
    lines = f.readlines()
    line = lines[0].split()
    user_public_key = [line[0], line[1]]
    line = lines[1].split()
    user_private_key = [line[0], line[1]]
    print("userpub", user_public_key)
    print("userpriv", user_private_key)


def generate_keys():
    global user_public_key
    global user_private_key
    user_public_key, user_private_key = RSA.rsa_key_generation()
    f = open(username + ".txt", "a")
    f.write("{n} {e}\n{n} {d}".format(n=user_public_key[0], e=user_public_key[1], d=user_private_key[1]))


def main():
    global user_public_key
    global user_private_key
    print("public: ", user_public_key)
    print("private: ", user_private_key)
    user_public_key, user_private_key = RSA.rsa_key_generation()
    console_application()


main()
