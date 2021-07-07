import pickle
import socket
import threading
import utils.rsa as RSA
from Database.db_manager import *

SERVER_HOST = 'localhost'
SERVER_PORT = 8080
server_private_key = [123, 33]
server_public_key = [123, 17]

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen()

connected_list=[]


def create_notifications(uploader_username,image_name):
    user_list = get_all_user()
    for user in user_list:
        add_notification(username=user.username,image_name=image_name,uploader_username=uploader_username)

def upload(message):
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
    print("aes-key decrypted", aes)
    iv = RSA.decrypt(public_key_encrypted_iv, server_private_key)
    mode = str(mode)
    size = str(size)
    encrypted_image = encrypted_image
    private_key_encrypted_digest = private_key_encrypted_digest
    insert_image(name=image_name, mode=mode, size=size, encrypted_image=encrypted_image,
                 uploader_name=uploader_username, aes=aes, iv=iv, digest=private_key_encrypted_digest)
    print("Image was sent")
    for client in connected_list:
        message={
            "type":"NOTIFICATION",
            "data":{
                "username":uploader_username,
                "image_name":image_name
            }
        }
        print(client[0])
        send(client[0],message)

    create_notifications(uploader_username,image_name)


def register(message):
    username = message["data"]["username"]
    user_public_key = message["data"]["public_key"]
    user_certificate = RSA.encrypt_int(user_public_key, server_private_key)
    if get_user(username) is None:
        insert_user(username=username, public_key=user_public_key, certificate=user_certificate)
        print("Registered user: ", username)


def login(message):
    username = message["data"]["username"]
    print(username, " is logon")


def download(client_connection, message):
    requester_username = message["data"]["username"]
    print("req_user",requester_username)
    requester_user = get_user(requester_username)
    image_name = message["data"]["image_name"]
    image = get_image(image_name)
    uploader_username = image.uploader_name
    uploader_user = get_user(uploader_username)
    uploader_certificate = uploader_user.certificate
    digest = image.digest
    upload_image_aes = image.aes
    upload_image_iv = image.iv
    encrypted_image = image.encrypted_image

    requester_public_key = requester_user.public_key
    requester_public_key_encrypted_aes = RSA.encrypt(upload_image_aes, requester_public_key)
    requester_public_key_encrypted_iv = RSA.encrypt(upload_image_iv, requester_public_key)

    message = {
        "type": "IMAGE_RECEIVED",
        "data": {
            "image_name": image_name,
            "encrypted_image": encrypted_image,
            "digest": digest,
            "certificate": uploader_certificate,
            "mode": image.mode,
            "size": image.size,
            "requester_public_key_encrypted_aes": requester_public_key_encrypted_aes,
            "requester_public_key_encrypted_iv": requester_public_key_encrypted_iv
        }
    }
    send(client_connection, message)


def server_response(client_connection, client_address):
    while True:
        message = recv(client_connection)
        if message["type"] == "REGISTER":
            register(message)
            message = {
                "type": "REGISTER SUCCESFUL"
            }
            send(client_connection, message)
        elif message["type"] == "LOGIN":
            login(message)
            message = {
                "type": "LOGIN SUCCESSFUL"
            }
            send(client_connection, message)
        elif message["type"] == "UPLOAD_IMAGE":
            upload(message)
            message = {
                "type": "UPLOAD SUCCESFUL"
            }
            send(client_connection, message)
        elif message["type"] == "DOWNLOAD_IMAGE":
            download(client_connection, message)
            message = {
                "type": "DOWNLOAD SUCCESFULLL"
            }
            send(client_connection, message)

        elif message["type"] == "NOTIFICATION_RECEIVED":
            received_user=message["data"]["received_user"]
            image_name = message["data"]["image_name"]
            del_notification(received_user,image_name)

        elif message["type"] == "GET_NOTIFICATIONS":
            username= message["username"]
            notifications=get_notifications(username)
            dict={}
            for notification in notifications:
                dict[notification.uploader_username]=notification.image_name

            message={
                "type": "NOTIFICATION_LIST",
                "notification_list" : dict
            }
            send(client_connection,message)
            del_notifications(username)

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
    global connected_list
    while True:
        client_connection, client_address = server_socket.accept()
        connected_list.append((client_connection,client_address))
        print(connected_list)
        threading.Thread(target=server_response, args=(client_connection, client_address)).start()


def main():
    print("public: ", server_public_key)
    print("private: ", server_private_key)
    listen()


main()
