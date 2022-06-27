import socket
import threading
import sys
import ssl
from time import sleep

host, port = server = ("0.0.0.0", 62113)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("new.pem", "private.key")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssock = context.wrap_socket(sock, server_side=True)
try:
    ssock.bind(server)
except socket.gaierror:
    sys.exit("Host not known!")
ssock.listen(5)
print("Server is listening..")
clients = []
nicknames = []


def cast(mode, message, nickname=None):
    if mode == "chat":
        for client in clients:
            client.send(f"{nickname.strip()}: ".encode("ascii") + message)

    elif mode == "broadcast":
        for client in clients:
            client.send(message)


def quit_msg(nickname, a, p):
    print(f"----------------------------------------------------\n"
          f"{nickname} with the following data has disconnected.\n"
          f"[Address: {a}, PORT: {p}]\n"
          f"----------------------------------------------------\n")


def handler(client, addr):
    while True:
        a, p = i = addr
        try:
            index = clients.index(client)
            nickname = nicknames[index]
            msg = client.recv(1024)
            if msg.decode("ascii").strip() == "/quit":
                clients.remove(client)
                client.close()
                cast("broadcast", f"\r{nickname.strip()} left the chat!\n".encode("ascii"), nickname)
                quit_msg(nickname, a, p)
                nicknames.remove(nickname)
                break
            else:
                sleep(0.3)
                cast("chat", msg, nickname)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            cast("broadcast", f"\r{nickname.strip()} left the chat!\n".encode("ascii"), nickname)
            quit_msg(nickname, a, p)
            nicknames.remove(nickname)
            break


def receive():
    while True:
        try:  # if no handshake was made. Connection is NOT accepted.
            client, addr = ssock.accept()
        except:
            continue
        print(f"Connected with {str(addr)}.")

        client.send("Nickname: ".encode("ascii"))

        nickname = client.recv(1024).decode("ascii")
        while nickname in nicknames or nickname.strip() == "":
            nickname = client.recv(1024).decode("ascii")
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of the client is {nickname}")
        client.send("Connected to the server!\n"
                    "--------------------------------\n"
                    "type '/quit' to exit the server.\n"
                    "--------------------------------\n\n"
                    .encode("ascii"))
        cast("broadcast", f"{nickname.strip()} joined the chat!\n".encode("ascii"), nickname)

        thread = threading.Thread(target=handler, args=(client, addr,))
        thread.start()
    sys.exit("Error. Server Closed.")


receive()
