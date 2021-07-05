import pickle
import socket
import threading
import utils.rsa as RSA
from Database.db_manager import *

SERVER_HOST = 'localhost'
SERVER_PORT = 8080
server_private_key = [205, 141]
server_public_key = [205, 101]

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen()


def server_response(client_connection, client_address):
    while True:
        message = recv(client_connection)
        if message["type"] == "REGISTER":
            username = message["data"]["username"]
            user_public_key = message["data"]["public_key"]
            user_certificate = RSA.encrypt_int(user_public_key, server_private_key)
            user_public_key = "" + str(user_public_key[0]) + " " + str(user_public_key[1])
            user_certificate = "" + str(user_certificate[0]) + " " + str(user_certificate[1])
            if get_user(username) is None:
                insert_user(username=username, public_key=user_public_key, certificate=user_certificate)
                print("Registered user: ", username)

        if message["type"] == "LOGIN":
            username = message["data"]["username"]
            print(username, " is logon")
        elif message["type"] == "UPLOAD_IMAGE":
            uploader_username = message["data"]["username"]
            print(uploader_username)
            image_name = message["data"]["image_name"]
            mode = message["data"]["mode"]
            size = message["data"]["size"]
            encrypted_image = message["data"]["encrypted_image"]
            private_key_encrypted_digest = message["data"]["private_key_encrypted_digest"]

            public_key_encrypted_aes = message["data"]["public_key_encrypted_aes"]
            public_key_encrypted_iv = message["data"]["public_key_encrypted_iv"]
            aes = RSA.decrypt(public_key_encrypted_aes, server_private_key)
            iv = RSA.decrypt(public_key_encrypted_iv, server_private_key)
            mode=str(mode)
            size=str(size)
            encrypted_image=bytes(encrypted_image)
            aes=str(aes)
            iv=str(iv)
            private_key_encrypted_digest=str(private_key_encrypted_digest)

            insert_image(name=image_name, mode=mode, size=size, encrypted_image=encrypted_image,
                         uploader_name=uploader_username, aes=aes, iv=iv, digest=private_key_encrypted_digest)


def send(client_connection, message):
    client_connection.send(pickle.dumps(message))
    print("Message is sent")


def recv(client_connection):
    data = b''
    l = 4096
    while l == 4096:
        d = client_connection.recv(l)
        l = len(d)
        data += d
    message = pickle.loads(data)
    return message


def listen():
    while True:
        client_connection, client_address = server_socket.accept()
        threading.Thread(target=server_response, args=(client_connection, client_address)).start()


def main():
    print("public: ", server_public_key)
    print("private: ", server_private_key)
    listen()


main()
