"""
TCP over SSL server.

to connect to this server 'remotely', add a port in your router/firewall
that allows traffic forwarding from public IP to localhost (on your Host machine)
start the server, and now you can connect (as a client) from
a command line on any operating system by
typing the following command:
$ openssl s_client -connect PUBLIC_IP:PORT
replace PUBLIC_IP and PORT with your server's.

##NOTE: openSSL must be installed in order to do a handshake with the server.
# be sure to create .pem file, private.key, ssl certificate to
load certificate chain.
"""

import socket
import threading
import sys
import ssl

host, port = server = ("0.0.0.0", 62113)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("new.pem", "private.key")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind(server)
except socket.gaierror:
    sys.exit("Host not known!")

sock.listen(5)
ssock = context.wrap_socket(sock, server_side=True)

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
        try:
            try:  # if no handshake was made. Connection is NOT accepted.
                client, addr = ssock.accept()
            except:
                continue
            print(f"Connected with {str(addr)}.")

            client.send("Nickname: ".encode("ascii"))

            nickname = client.recv(1024).decode("ascii")
            while nickname in nicknames:
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
        except KeyboardInterrupt:
            for client in clients:
                try:
                    client.close()
                except:
                    continue
            break
    sys.exit("Error. Server Closed.")


receive()
