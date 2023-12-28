import socket
import threading
import time
from datetime import datetime, timedelta

def connection(host, port, server_socket):
    global active
    global clients
    global client_conn
    global salons
    global client_salon
    global sanction_kick
    global sanction_ban
    global superusers
    global admin_salon
    global salon_acces
    global salon_request
    global accounts
    global aliases

    active = True
    clients = []
    client_threads = []
    client_conn = {}

    salons = ["Général", "Blabla", "Comptabilité", "Informatique", "Marketing"]
    client_salon = {"Général":[], "Blabla":[], "Comptabilité":[], "Informatique":[], "Marketing":[]}

    sanction_kick = {}
    sanction_ban = []
    superusers = ["joshua", "toto"]
    admin_salon = {"Général":"none", "Blabla":"server", "Comptabilité":"admin_compta", "Informatique":"admin_info", "Marketing":"admin_market"}
    salon_acces = {"Général":[], "Blabla":[], "Comptabilité":[admin_salon["Comptabilité"]], "Informatique":[admin_salon["Informatique"]], "Marketing":[admin_salon["Marketing"]]}
    salon_request = {admin_salon["Blabla"]:[], admin_salon["Comptabilité"]:[], admin_salon["Informatique"]:[], admin_salon["Marketing"]:[]}

    accounts = {"joshua":"1234", 
                "toto":"admin", 
                "ayrton":"maradan", 
                "olivier":"guittet",
                "admin_compta":"test1",
                "admin_info":"test2",
                "admin_market":"test3"}

    aliases = {"joshua":"JOSHUA",
               "toto":"SERVER_ADMIN",
               "ayrton":"AYRTON",
               "olivier":"OLIVIER",
               "admin_compta":"George",
               "admin_info":"Alex",
               "admin_market":"Clara"}

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
    global client_conn
    global salons
    global client_salon
    global sanction_kick
    global sanction_ban
    global salon_acces
    global salon_request
    global accounts
    global aliases

    flag = True
    flag_all = True
    ok = False
    account_done = False
    pseudo_ok = False

    while account_done != True:
        time.sleep(0.5)
        conn.send("account_exist".encode())
        account_exists = conn.recv(1024).decode().lower()
        if account_exists == "yes" or account_exists == "y":
            conn.send("initiate".encode())
            while ok != True:
                time.sleep(1)
                conn.send("serveur_login".encode())
                login = conn.recv(1024).decode()
                conn.send("serveur_password".encode())
                password = conn.recv(1024).decode()
                if login in client_conn.values():
                    conn.send("erroneous_account".encode())
                elif login in accounts:
                    if password == accounts[login]:
                        client_conn[conn] = login
                        if login in aliases:
                            conn.send("recv_pseudo".encode())
                            time.sleep(0.5)
                            conn.send(aliases[login].encode())
                            time.sleep(0.5)
                            conn.send("account_validated".encode())
                            ok = True
                        elif login not in aliases:
                            conn.send("account_pseudo".encode())
                            while pseudo_ok != True:
                                pseudo = conn.recv(1024).decode()
                                if pseudo in aliases.values():
                                    conn.send("pseudo_used".encode())
                                else:
                                    conn.send("account_validated".encode())
                                    aliases[login] = pseudo
                                    pseudo_ok = True
                                    ok = True
                    elif password != accounts[login]:
                        conn.send("erroneous_account".encode())
                elif login not in accounts:
                    conn.send("erroneous_account".encode())
            account_done = True
        elif account_exists == "no" or account_exists == "n":
            conn.send("initiate".encode())
            while account_done != True:
                time.sleep(0.5)

                conn.send("serveur_login".encode())
                login = conn.recv(1024).decode()
                conn.send("serveur_password".encode())
                password = conn.recv(1024).decode()

                if login in accounts:
                    conn.send("erroneous_account".encode())
                else:
                    conn.send("account_pseudo".encode())
                    pseudo = conn.recv(1024).decode()
                    if pseudo in aliases.values():
                        conn.send("pseudo_used".encode())
                    else:
                        accounts[login] = password
                        client_conn[conn] = login
                        aliases[login] = pseudo
                        account_done = True
                        conn.send("account_validated".encode())        
        else:
            conn.send("account_restart".encode())

    pseudo = aliases[login]

    client_salon["Général"].append(conn)
    salon = "Général"
    if login not in salon_acces[salon]:
        salon_acces[salon].append(login)

    if login in sanction_ban:
        reply = f"Ce compte est ban permanément"
        conn.send(reply.encode())
        time.sleep(0.5)
        reply = "server disconnection"
        conn.send(reply.encode())
        flag = False
    elif login in sanction_kick:
        current_time = datetime.now()
        if sanction_kick[login] > current_time:
            reply = f"Ce compte est ban jusqu'à {sanction_kick[login]}"
            conn.send(reply.encode())
            time.sleep(0.5)
            reply = "server disconnection"
            conn.send(reply.encode())
            flag = False

    while flag != False and flag_all != False:
        try:
            msg = conn.recv(1024).decode()
        except OSError:
            msg = ""
        print(f"[{salon}] {pseudo} > {msg}")
        if msg == "/bye":
            flag = False
            reply = "server disconnection"
            conn.send(reply.encode())
        elif msg == "/kill" and client_conn[conn] in superusers:
            for client in clients:
                client.send("server disconnection".encode())                
            flag_all = False
            active = False
        elif msg.startswith("/kill") and client_conn[conn] not in superusers:
            reply = "Vous n'êtes pas autorisé à utiliser la commande /kill"
            conn.send(reply.encode())
        elif msg.startswith("/kick") and client_conn[conn] in superusers:
            command = msg.split(" ")
            if command[1].startswith("@"):
                target_pseudo = command[1][1:]
                for k, v in aliases.items():
                    if v == target_pseudo:
                        target_login = k
                if target_login in accounts:
                    current_time = datetime.now()
                    release_time = current_time + timedelta(hours=1)
                    sanction_kick[f"{target_login}"] = release_time
                    for k, v in client_conn.items():
                        if v == target_login:
                            k.send("server disconnection".encode())
                    reply = f"/!\ L'utilisateur {target_pseudo} a été ban jusqu'à {release_time}"
                    conn.send(reply.encode())
                elif target_login not in accounts:
                    reply = f"/!\ L'utilisateur {target_pseudo} n'existe pas"
                    conn.send(reply.encode())
        elif msg.startswith("/kick") and client_conn[conn] not in superusers:
            reply = "Vous n'êtes pas autorisé à utiliser la commande /kick"
            conn.send(reply.encode())
        elif msg.startswith("/ban") and client_conn[conn] in superusers:
            command = msg.split(" ")
            if command[1].startswith("@"):
                target_pseudo = command[1][1:]
                for k, v in aliases.items():
                    if v == target_pseudo:
                        target_login = k
                if target_login in accounts:
                    sanction_ban.append(target_login)
                    for k, v in client_conn.items():
                        if v == target_login:
                            k.send("server disconnection".encode())
                    reply = f"/!\ L'utilisateur {target_pseudo} a été ban indéfiniment"
                    conn.send(reply.encode())
                elif target_login not in accounts:
                    reply = f"/!\ L'utilisateur {target_pseudo} n'existe pas"
                    conn.send(reply.encode())
        elif msg.startswith("/ban") and client_conn[conn] not in superusers:
            reply = "Vous n'êtes pas autorisé à utiliser la commande /ban"
            conn.send(reply.encode())
        elif msg.startswith("/access"):
            command = msg.split(" ")
            if len(command) == 2:
                if command[1].startswith("salon_"):
                    target = command[1][6:]
                    if login not in salon_acces[target]:
                        if target == "Blabla":
                            reply = f"Pour accéder à ce salon, vous devez faire une requête à server"
                            conn.send(reply.encode())
                        else:
                            reply = f"Pour accéder à ce salon, vous devez faire une requête à {aliases[admin_salon[target]]}"
                            conn.send(reply.encode())
                    else:
                        client_salon[salon].remove(conn)
                        salon = target
                        client_salon[salon].append(conn)
            elif len(command) == 3:
                if command[1].startswith("salon_") and command[2].startswith("@"):
                    target_pseudo = command[2][1:]
                    for k, v in aliases.items():
                        if v == target_pseudo:
                            target_login = k
                    if target_pseudo == admin_salon["Blabla"]:
                        salon_acces["Blabla"].append(login)
                        reply = "Accès au salon 'Blabla' accordé"
                        conn.send(reply.encode())
                    elif target_login == admin_salon[command[1][6:]]:
                        reply = f"Une requête à été faite auprès de {target_pseudo} pour accéder au salon {command[1][6:]}"
                        conn.send(reply.encode())
                        salon_request[target_login].append(pseudo)
        elif msg == "/requests" and login in admin_salon.values():
            reply = f"Requêtes pour l'utilisateur {pseudo}:\n"
            for i in range(len(salon_request[login])):
                reply+= f" {salon_request[login][i]} |"
            reply = reply[:-2]
            conn.send(reply.encode())
        elif msg.startswith("/accept_request@") and login in admin_salon.values():
            command = msg.split("@")
            user_pseudo = command[1]
            for k, v in aliases.items():
                if v == user_pseudo:
                    user_login = k
            if user_pseudo in salon_request[login]:
                for indiv_salon in admin_salon:
                    if admin_salon[indiv_salon] == login:
                        if user_login not in salon_acces[indiv_salon]:
                            salon_acces[indiv_salon].append(user_login)
                            for id in client_conn:
                                if client_conn[id] == user_login:
                                    reply = f"Votre accès au salon {indiv_salon} a été permis"
                                    id.send(reply.encode())
                        else:
                            reply = f"L'utilisateur {user_pseudo} a déjà accés au salon {indiv_salon}"
            else:
                reply = f"L'utilisateur {user_pseudo} n'a pas émis de requêtes"
                conn.send(reply.encode())
        elif msg.startswith("/deny_request@") and login in admin_salon.values():
            command = msg.split("@")
            user_pseudo = command[1]
            for k, v in aliases.items():
                if v == user_pseudo:
                    user_login = k
            if user_pseudo in salon_request[login]:
                for indiv_salon in admin_salon:
                    if admin_salon[indiv_salon] == login:
                        if user_login not in salon_acces[indiv_salon]:
                            salon_request[login].remove(user_pseudo)
                            for id in client_conn:
                                if client_conn[id] == user_login:
                                    reply = f"Votre accès au salon {indiv_salon} a été refusé"
                                    id.send(reply.encode())
                        else:
                            reply = f"L'utilisateur {user_pseudo} a déjà accés au salon {indiv_salon}"
            else:
                reply = f"L'utilisateur {user_pseudo} n'a pas émis de requêtes"
                conn.send(reply.encode())
        elif msg == "/salons":
            list_salons = f"|{str(salons)}|"
            conn.send(list_salons.encode())
        elif msg != "":
            for client in client_salon[salon]:
                if client_conn[client] != "":
                    client.send(f"[{salon}] {pseudo} > {msg}".encode())
        elif msg == "":
            flag = False

    conn.close()
    clients.remove(conn)

    del client_conn[conn]

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