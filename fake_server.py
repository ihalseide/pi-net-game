#!/usr/bin/env python3

import socket

sock = socket.create_server(('localhost', 7777), family=socket.AF_INET, backlog=1)
while True:
    print("listening...")
    (client_sock, client_addr) = sock.accept()
    print("got one!")
    print(client_sock.recv(20))
    client_sock.sendall(b"00010server_yes")
    client_sock.close()