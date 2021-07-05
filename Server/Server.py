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
        print("slm")
        if message["type"] == "REGISTER":
            username = message["data"]["username"]
            if get_user(username) is None:
                user_public_key = message["data"]["public_key"]
                user_certificate = RSA.encrypt_int(user_public_key, server_private_key)
                user_public_key = "" + str(user_public_key[0]) + " " + str(user_public_key[1])
                user_certificate = "" + str(user_certificate[0]) + " " + str(user_certificate[1])
                insert_user(username=username, public_key=user_public_key, certificate=user_certificate)
                print("Registered user: ", username)
            print(get_user("serkan").public_key[0])


def send(client_connection, message):
    client_connection.send(pickle.dumps(message))
    print("Message is sent")


def recv(client_connection):
    message = pickle.loads(client_connection.recv(4096))
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
