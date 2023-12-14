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
    global superusers
    global admin_salon
    global salon_acces
    global salon_request

    active = True
    clients = []
    client_threads = []
    client_pseudo = {}

    salons = ["Général", "Blabla", "Comptabilité", "Informatique", "Marketing"]
    client_salon = {"Général":[], "Blabla":[], "Comptabilité":[], "Informatique":[], "Marketing":[]}

    sanction_kick = {}
    sanction_ban = []
    superusers = ["joshua", "toto"]
    admin_salon = {"Général":"none", "Blabla":"server", "Comptabilité":"admin_compta", "Informatique":"admin_info", "Marketing":"admin_market"}
    salon_acces = {"Général":[], "Blabla":[], "Comptabilité":[admin_salon["Comptabilité"]], "Informatique":[admin_salon["Informatique"]], "Marketing":[admin_salon["Marketing"]]}
    salon_request = {admin_salon["Blabla"]:[], admin_salon["Comptabilité"]:[], admin_salon["Informatique"]:[], admin_salon["Marketing"]:[]}

    while active != False:
        try:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=receive, args=[conn, addr])
            clients.append(conn)
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
    global salon_acces
    global salon_request

    flag = True
    flag_all = True
    ok = False

    time.sleep(3)

    conn.send("serveur_pseudo".encode())
    while ok != True:
        identifiant = conn.recv(1024).decode()
        if identifiant in client_pseudo.values():
            conn.send("pseudo_not_allowed".encode())
        else:
            conn.send("pseudo_validated".encode())
            client_pseudo[conn] = identifiant
            ok = True

    time.sleep(2)

    client_salon["Général"].append(conn)
    salon = "Général"
    if identifiant not in salon_acces[salon]:
        salon_acces[salon].append(identifiant)

    if identifiant in sanction_kick:
        current_time = datetime.now()
        if sanction_kick[f"{identifiant}"] > current_time:
            reply = f"Ce compte est ban jusqu'à {sanction_kick[f'{identifiant}']}"
            conn.send(reply.encode())
            time.sleep(2)
            reply = "server disconnection"
            conn.send(reply.encode())
            flag = False
    if identifiant in sanction_ban:
        reply = f"Ce compte est ban permanément"
        conn.send(reply.encode())
        time.sleep(2)
        reply = "server disconnection"
        conn.send(reply.encode())
        flag = False

    while flag != False and flag_all != False:
        try:
            msg = conn.recv(1024).decode()
        except OSError:
            msg = ""
        print(f"[{salon}] {identifiant} > {msg}")
        if msg == "bye":
            flag = False
            reply = "server disconnection"
            conn.send(reply.encode())
        elif msg == "stop":
            for client in clients:
                client.send("server disconnection".encode())                
            flag_all = False
            active = False
        elif msg.startswith("/kick") and client_pseudo[conn] in superusers:
            command = msg.split(" ")
            if command[1].startswith("@"):
                target = command[1][1:]
                current_time = datetime.now()
                release_time = current_time + timedelta(hours=1)
                sanction_kick[f"{target}"] = release_time
                for k, v in client_pseudo.items():
                    if v == target:
                        k.send("server disconnection".encode())
        elif msg.startswith("/kick") and client_pseudo[conn] not in superusers:
            reply = "Vous n'êtes pas autorisé à utiliser la commande /kick"
            conn.send(reply.encode())
        elif msg.startswith("/ban") and client_pseudo[conn] in superusers:
            command = msg.split(" ")
            if command[1].startswith("@"):
                target = command[1][1:]
                sanction_ban.append(target)
                for k, v in client_pseudo.items():
                    if v == target:
                        k.send("server disconnection".encode())
        elif msg.startswith("/ban") and client_pseudo[conn] not in superusers:
            reply = "Vous n'êtes pas autorisé à utiliser la commande /ban"
            conn.send(reply.encode())
        elif msg.startswith("/access"):
            command = msg.split(" ")
            if len(command) == 2:
                if command[1].startswith("salon_"):
                    target = command[1][6:]
                    if identifiant not in salon_acces[target]:
                        reply = f"Pour accéder à ce salon, vous devez faire une requête à {admin_salon[target]}"
                        conn.send(reply.encode())
                    else:
                        client_salon[salon].remove(conn)
                        salon = target
                        client_salon[salon].append(conn)
            elif len(command) == 3:
                if command[1].startswith("salon_") and command[2].startswith("@"):
                    target = command[2][1:]
                    if target == admin_salon["Blabla"]:
                        salon_acces["Blabla"].append(identifiant)
                        reply = "Accès au salon 'Blabla' accordé"
                        conn.send(reply.encode())
                    elif target == admin_salon[command[1][6:]]:
                        reply = f"Une requête à été faite auprès de {target} pour accéder au salon {command[1][6:]}"
                        conn.send(reply.encode())
                        salon_request[target].append(identifiant)
        elif msg == "requests" and identifiant in admin_salon.values():
            reply = f"Requêtes pour l'utilisateur {identifiant}:\n"
            for i in range(len(salon_request[identifiant])):
                reply+= f" {salon_request[identifiant][i]} |"
            reply = reply[:-2]
            conn.send(reply.encode())
        elif msg.startswith("accept_request@") and identifiant in admin_salon.values():
            command = msg.split("@")
            if command[1] in salon_request[identifiant]:
                for indiv_salon in admin_salon:
                    if admin_salon[indiv_salon] == identifiant:
                        if command[1] not in salon_acces[indiv_salon]:
                            salon_acces[indiv_salon].append(command[1])
                            for id in client_pseudo:
                                if client_pseudo[id] == command[1]:
                                    reply = f"Votre accès au salon {indiv_salon} a été permis"
                                    id.send(reply.encode())
                        else:
                            reply = f"L'utilisateur {command[1]} a déjà accés au salon {indiv_salon}"
            else:
                reply = f"L'utilisateur {command[1]} n'a pas émis de requêtes"
                conn.send(reply.encode())
        elif msg.startswith("deny_request@") and identifiant in admin_salon.values():
            command = msg.split("@")
            if command[1] in salon_request[identifiant]:
                for indiv_salon in admin_salon:
                    if admin_salon[indiv_salon] == identifiant:
                        if command[1] not in salon_acces[indiv_salon]:
                            salon_request[identifiant].remove(command[1])
                            for id in client_pseudo:
                                if client_pseudo[id] == command[1]:
                                    reply = f"Votre accès au salon {indiv_salon} a été refusé"
                                    id.send(reply.encode())
                        else:
                            reply = f"L'utilisateur {command[1]} a déjà accés au salon {indiv_salon}"
            else:
                reply = f"L'utilisateur {command[1]} n'a pas émis de requêtes"
                conn.send(reply.encode())
        elif msg == "salons":
            list_salons = f"|{str(salons)}|"
            conn.send(list_salons.encode())
        elif msg != "":
            for client in client_salon[salon]:
                if client != conn and client_pseudo[client] != "":
                    client.send(f"[{salon}] {identifiant} > {msg}".encode())
        elif msg == "":
            flag = False

    conn.close()
    clients.remove(conn)

    del client_pseudo[conn]

    client_salon[salon].remove(conn)

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