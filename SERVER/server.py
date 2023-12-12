import socket
import threading
import time
from datetime import datetime, timedelta

def connection(host, port, server_socket):
    global active
    global clients
    global client_pseudo
    global salons
    global client_salon
    global sanction_kick
    global sanction_ban

    active = True
    clients = []
    client_threads = []
    client_pseudo = {}

    salons = ["Général", "Blabla", "Comptabilité", "Informatique", "Marketing"]
    client_salon = {}
    for i in range(len(salons)):
        client_salon[f"{salons[i]}"] = []

    sanction_kick = {}
    sanction_ban = []

    while active != False:
        try:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=receive, args=[conn, addr])
            clients.append(conn)
            client_pseudo[f"{conn}"] = ""
            client_threads.append(client_thread)
            client_thread.start()
        except socket.timeout:
            pass
    
    for client_thread in client_threads:
        client_thread.join()
    
    print("server shutdown")

def receive(conn, addr):
    global active
    global flag_all
    global client_pseudo
    global salons
    global client_salon
    global sanction_kick
    global sanction_ban

    flag = True
    flag_all = True
    ok = False
    connection = str(conn)

    time.sleep(3)

    conn.send("serveur_pseudo".encode())
    while ok != True:
        identifiant = conn.recv(1024).decode()
        if identifiant in client_pseudo.values():
            conn.send("pseudo_not_allowed".encode())
        else:
            conn.send("pseudo_validated".encode())
            client_pseudo[f"{conn}"] = identifiant
            ok = True

    client_salon["Général"].append(conn)
    salon = "Général"

    if identifiant in sanction_kick:
        if sanction_kick[f"{identifiant}"] > datetime.now():
            reply = f"You are banned until {sanction_kick[f'{identifiant}']}"
            conn.send(reply.encode())
            time.sleep(2)
            conn.send("server disconnection".encode())
            conn.close()
            index_conn = clients.index(conn)
            clients.pop(index_conn)
            flag = False

    while flag != False and flag_all != False:
        msg = conn.recv(1024).decode()
        print(f"[{salon}] {identifiant} > {msg}")
        if msg == "bye":
            flag = False
            reply = "server disconnection"
            conn.send(reply.encode())
            conn.close()
            index_conn = clients.index(conn)
            clients.pop(index_conn)
        elif msg == "stop":
            flag_all = False
            for client in clients:
                client.send("server disconnection".encode())
                time.sleep(2)
            active = False
        elif msg.startswith("/kick"):
            command = msg.split(" ")
            if command[1].startswith("@"):
                target = command[1][1:]
                current_time = datetime.now()
                release_time = current_time + timedelta(hours=1)
                sanction_kick[f"{target}"] = release_time
        elif msg == "salons":
            list_salons = f"|{str(salons)}|"
            conn.send(list_salons.encode())
        elif msg in salons:
            index = client_salon[f"{salon}"].index(conn)
            client_salon[f"{salon}"].pop(index)
            salon = msg
            client_salon[f"{salon}"].append(conn)
        else:
            for client in client_salon[f"{salon}"]:
                if client != conn and client_pseudo[f"{client}"] != "":
                    client.send(f"[{salon}] {identifiant} > {msg}".encode())
    
    del client_pseudo[f"{connection}"]
    index = client_salon[f"{salon}"].index(conn)
    client_salon[f"{salon}"].pop(index)

def main():
    host = '0.0.0.0'
    port = 10000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(10)
    server_socket.settimeout(3.0)

    wait_co = threading.Thread(target=connection, args=[host, port, server_socket])
    wait_co.start()

    wait_co.join()

    time.sleep(2)
    server_socket.close()

if __name__ == '__main__':
    main()