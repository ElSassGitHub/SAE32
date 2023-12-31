#create user 'server'@'localhost' identified by 'SAE32';
#grant all privileges on Elsass_Chat.* to server@localhost;
#flush privileges;

import socket
import threading
import time
from datetime import datetime, timedelta
import MySQLdb

def register_msg(msg, login, salon):
    query = f"SELECT id_compte FROM Comptes WHERE login='{login}'"
    cursor.execute(query)
    result = cursor.fetchall()
    id_compte = result[0][0]

    query = f"SELECT id_salon FROM Salon WHERE nom_salon='{salon}'"
    cursor.execute(query)
    result = cursor.fetchall()
    nom_salon = result[0][0]

    current_time = datetime.now()
    query = "INSERT INTO Messages (content, date, compte, salon) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (msg, current_time, id_compte, nom_salon))
    connection.commit()
    print("done")

def check_database():
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
    global account_IP
    global cursor
    global connection

    query = "SELECT Comptes.login, Sanctions.date FROM Sanctions INNER JOIN Comptes ON Sanctions.compte=Comptes.id_compte WHERE type='kick'"
    cursor.execute(query)
    result = cursor.fetchall()
    for i in range(len(result)):
        sanction_kick[result[i][0]] = result[i][1]
    
    query = "SELECT Comptes.login, Sanctions.date FROM Sanctions INNER JOIN Comptes ON Sanctions.compte=Comptes.id_compte WHERE type='ban'"
    cursor.execute(query)
    result = cursor.fetchall()
    for i in range(len(result)):
        sanction_ban.append(result[i][0])

    query = "SELECT distinct(login) FROM Comptes INNER JOIN Autorisations ON Comptes.id_compte=Autorisations.compte WHERE niv_auto=3"
    cursor.execute(query)
    result = cursor.fetchall()
    for i in range(len(result)):
        superusers.append(result[0][0])

    query = "SELECT Comptes.login, Salon.nom_salon FROM Comptes INNER JOIN Autorisations ON Comptes.id_compte=Autorisations.compte INNER JOIN Salon ON Autorisations.salon=Salon.id_salon WHERE Autorisations.niv_auto=2"
    cursor.execute(query)
    result = cursor.fetchall()
    for i in range(len(result)):
        admin_salon[result[i][1]] = result[i][0]
        
    query = "SELECT Requetes.admin, Comptes.pseudo FROM Requetes INNER JOIN Comptes ON Requetes.compte=Comptes.id_compte"
    cursor.execute(query)
    result = cursor.fetchall()
    for i in range(len(result)):
        query = f"SELECT login FROM Comptes WHERE id_compte={result[i][0]}"
        cursor.execute(query)
        result2 = cursor.fetchall()
        if result[i][1] not in salon_request[f"{result2[i][0]}"]:
            salon_request[f"{result2[i][0]}"].append(result[i][1])

    query = "SELECT Comptes.login, Salon.nom_salon FROM Comptes INNER JOIN Autorisations ON Comptes.id_compte=Autorisations.compte INNER JOIN Salon ON Autorisations.salon=Salon.id_salon WHERE Autorisations.niv_auto>0"
    cursor.execute(query)
    result = cursor.fetchall()
    for i in range(len(result)):
        salon_acces[result[i][1]].append(result[i][0])    

    query = "SELECT login, mdp, pseudo FROM Comptes"
    cursor.execute(query)
    result = cursor.fetchall()
    for i in range(len(result)):
        accounts[result[i][0]] = result[i][1]
        aliases[result[i][0]] = result[i][2]

    query = "SELECT Comptes.login, IP.IP FROM Comptes INNER JOIN IP ON Comptes.id_compte=IP.compte"
    cursor.execute(query)
    result = cursor.fetchall()
    for i in range(len(result)):
        account_IP[result[i][0]] = result[i][1]

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
    global account_IP
    global cursor
    global connection

    connection = MySQLdb.connect(
        host="127.0.0.1",
        user="server",
        password="SAE32",
        database="Elsass_Chat"
    )

    cursor = connection.cursor()

    active = True
    clients = []
    client_threads = []
    client_conn = {}

    salons = []
    client_salon = {}
    salon_acces = {}
    query = "SELECT * FROM Salon"
    cursor.execute(query)
    result = cursor.fetchall()
    for i in range(len(result)):
        salons.append(result[i][1])
        client_salon[result[i][1]] = []
        salon_acces[result[i][1]] = []

    sanction_kick = {}
    sanction_ban = []
    superusers = []
    admin_salon = {salons[0]:"none", salons[1]:"server"}

    salon_request = {admin_salon[salons[1]]:[]}
    query = f"SELECT Comptes.login FROM Comptes INNER JOIN Autorisations ON Comptes.id_compte=Autorisations.compte WHERE Autorisations.niv_auto=2"
    cursor.execute(query)
    result = cursor.fetchall()
    for i in range(len(result)):
        salon_request[result[i][0]] = []

    accounts = {}
    aliases = {}
    account_IP = {}

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
    
    cursor.close()
    connection.close()
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
    global account_IP
    global cursor
    global connection

    flag = True
    flag_all = True
    ok = False
    account_done = False

    check_database()

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
                        conn.send("recv_pseudo".encode())
                        time.sleep(0.5)
                        conn.send(aliases[login].encode())
                        time.sleep(0.5)
                        conn.send("account_validated".encode())
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
                        query = "INSERT INTO Comptes (login, mdp, pseudo, salon) VALUES(%s, %s, %s, 1)"
                        cursor.execute(query, (login, password, pseudo))
                        connection.commit()

                        query = f"SELECT id_compte FROM Comptes WHERE login='{login}'"
                        cursor.execute(query)
                        result = cursor.fetchall()
                        id_compte = result[0][0]

                        query = "INSERT INTO Autorisations (compte, salon, niv_auto) VALUES (%s, %s, %s)"
                        cursor.execute(query, (id_compte, 1, 1))
                        connection.commit()

                        client_conn[conn] = login

                        account_done = True
                        conn.send("account_validated".encode())    
                        check_database()    
        else:
            conn.send("account_restart".encode())

    addr = addr[0]
    if (login, addr) not in account_IP.items():
        query = f"SELECT id_compte FROM Comptes WHERE login='{login}'"
        cursor.execute(query)
        result = cursor.fetchall()
        id_compte = result[0][0]

        query = "INSERT INTO IP (IP, compte) VALUES (%s, %s)"
        cursor.execute(query, (str(addr), id_compte))
        connection.commit()

    pseudo = aliases[login]

    query = "SELECT login, mdp, pseudo FROM Comptes"
    cursor.execute(query)
    result = cursor.fetchall()
    for i in range(len(result)):
        accounts[result[i][0]] = result[i][1]
        aliases[result[i][0]] = result[i][2]
    
    query = f"SELECT Salon.nom_salon FROM Salon INNER JOIN Comptes on Salon.id_salon=Comptes.salon WHERE Comptes.login='{login}'"
    cursor.execute(query)
    result = cursor.fetchall()
    salon = result[0][0]

    client_salon[salon].append(conn)

    print(sanction_kick)
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
        check_database()
        try:
            msg = conn.recv(1024).decode()
        except OSError:
            msg = ""
        print(f"[{salon}] {pseudo} > {msg}")
        if msg == "/bye":
            flag = False
            reply = "server disconnection"
            conn.send(reply.encode())
        elif msg == "/kill" and client_conn[conn] in superusers and addr == "127.0.0.1":
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
                if target_pseudo in aliases:
                    query = f"SELECT login FROM Comptes WHERE pseudo='{target_pseudo}'"
                    cursor.execute(query)
                    result = cursor.fetchall()
                    target_login = result[0][0]
                    if target_login in accounts:
                        current_time = datetime.now()
                        release_time = current_time + timedelta(hours=1)
                        query = f"SELECT id_compte FROM Comptes WHERE login='{target_login}'"
                        cursor.execute(query)
                        result = cursor.fetchall()
                        id_compte = result[0][0]
                        query = "INSERT INTO Sanctions (compte, IP, date, type) VALUES (%s, %s, %s, 'kick')"
                        cursor.execute(query, (id_compte, account_IP[target_login], release_time))
                        connection.commit()
                        for k, v in client_conn.items():
                            if v == target_login:
                                k.send("server disconnection".encode())
                        reply = f"/!\ L'utilisateur {target_pseudo} a été ban jusqu'à {release_time}"
                        conn.send(reply.encode())
                    elif target_login not in accounts:
                        reply = f"/!\ L'utilisateur {target_pseudo} n'existe pas"
                        conn.send(reply.encode())
                elif target_pseudo in account_IP.values():
                    target_IP = target_pseudo
                    query = f"SELECT compte FROM IP WHERE IP.IP='{target_IP}'"
                    cursor.execute(query)
                    result = cursor.fetchall()
                    associated_IPs = []
                    for i in range(len(result)):
                        associated_IPs.append(result[i][0])
                    if target_IP in associated_IPs:
                        current_time = datetime.now()
                        release_time = current_time + timedelta(hours=1)
                        query = "INSERT INTO Sanctions (compte, IP, date, type) VALUES (%s, %s, %s, 'kick')"
                        for i in associated_IPs:
                            cursor.execute(query, (associated_IPs[i], target_IP, release_time))
                        connection.commit()
                        for k, v in client_conn.items():
                            if v == target_login:
                                k.send("server disconnection".encode())
                        reply = f"/!\ L'adress {target_IP} a été ban jusqu'à {release_time}"
                        conn.send(reply.encode())
                    elif target_login not in associated_IPs:
                        reply = f"/!\ Aucun compte n'est associé à l'adresse {target_IP}"
                        conn.send(reply.encode())
        elif msg.startswith("/kick") and client_conn[conn] not in superusers:
            reply = "Vous n'êtes pas autorisé à utiliser la commande /kick"
            conn.send(reply.encode())
        elif msg.startswith("/unkick") and client_conn[conn] in superusers:
            command = msg.split(" ")
            if command[1].startswith("@"):
                target_pseudo = command[1][1:]
                if target_pseudo in aliases:
                    query = f"SELECT login FROM Comptes WHERE pseudo='{target_pseudo}'"
                    cursor.execute(query)
                    result = cursor.fetchall()
                    target_login = result[0][0]
                    if target_login in sanction_kick:
                        query = f"SELECT id_compte FROM Comptes WHERE login='{target_login}'"
                        cursor.execute(query)
                        result = cursor.fetchall()
                        id_compte = result[0][0]
                        query = f"DELETE FROM Sanctions WHERE compte='{id_compte}'"
                        cursor.execute(query)
                        connection.commit()
                        reply = f"/!\ Le ban de l'utilisateur {target_pseudo} a été annulé"
                        conn.send(reply.encode())
                    elif target_login not in sanction_kick:
                        reply = f"/!\ L'utilisateur {target_pseudo} n'est pas sous l'effet d'un ban"
                        conn.send(reply.encode())
                elif target_pseudo in account_IP.values():
                    target_IP = target_pseudo
                    query = f"SELECT IP FROM Sanctions WHERE type='kick'"
                    cursor.execute(query)
                    result = cursor.fetchall()
                    IP_kick = result[0][0]
                    if target_IP in IP_kick:
                        query = f"DELETE FROM Sanctions WHERE IP.IP='{target_IP}'"
                        cursor.execute(query)
                        connection.commit()
                        reply = f"/!\ Le ban de l'adresse {target_IP} a été annulé"
                        conn.send(reply.encode())
                    elif target_IP not in IP_kick:
                        reply = f"/!\ L'adresse {target_IP} n'est pas sous l'effet d'un ban"
                        conn.send(reply.encode())
        elif msg.startswith("/unkick") and client_conn[conn] not in superusers:
            reply = "Vous n'êtes pas autorisé à utiliser la commande /unkick"
            conn.send(reply.encode())
        elif msg.startswith("/ban") and client_conn[conn] in superusers:
            command = msg.split(" ")
            if command[1].startswith("@"):
                target_pseudo = command[1][1:]
                if target_pseudo in aliases:
                    query = f"SELECT login FROM Comptes WHERE pseudo='{target_pseudo}'"
                    cursor.execute(query)
                    result = cursor.fetchall()
                    target_login = result[0][0]
                    if target_login in accounts:
                        query = f"SELECT id_compte FROM Comptes WHERE login='{target_login}'"
                        cursor.execute(query)
                        result = cursor.fetchall()
                        id_compte = result[0][0]
                        query = "INSERT INTO Sanctions (compte, IP, type) VALUES (%s, %s, 'ban')"
                        cursor.execute(query, (id_compte, account_IP[target_login]))
                        connection.commit()
                        sanction_ban.append(target_login)
                        for k, v in client_conn.items():
                            if v == target_login:
                                k.send("server disconnection".encode())
                        reply = f"/!\ L'utilisateur {target_pseudo} a été ban indéfiniment"
                        conn.send(reply.encode())
                    elif target_login not in accounts:
                        reply = f"/!\ L'utilisateur {target_pseudo} n'existe pas"
                        conn.send(reply.encode())
                elif target_pseudo in account_IP.values():
                    target_IP = target_pseudo
                    query = f"SELECT compte FROM IP WHERE IP.IP='{target_IP}'"
                    cursor.execute(query)
                    result = cursor.fetchall()
                    associated_IPs = []
                    for i in range(len(result)):
                        associated_IPs.append(result[i][0])
                    if target_IP in associated_IPs:
                        query = "INSERT INTO Sanctions (compte, IP type) VALUES (%s, %s, %s, 'ban')"
                        for i in associated_IPs:
                            cursor.execute(query, (associated_IPs[i], target_IP, release_time))
                        connection.commit()
                        for k, v in client_conn.items():
                            if v == target_login:
                                k.send("server disconnection".encode())
                        reply = f"/!\ L'adress {target_IP} a été ban indéfinitivement"
                        conn.send(reply.encode())
                    elif target_login not in associated_IPs:
                        reply = f"/!\ Aucun compte n'est associé à l'adresse {target_IP}"
                        conn.send(reply.encode())
        elif msg.startswith("/ban") and client_conn[conn] not in superusers:
            reply = "Vous n'êtes pas autorisé à utiliser la commande /ban"
            conn.send(reply.encode())
        elif msg.startswith("/unban") and client_conn[conn] in superusers:
            command = msg.split(" ")
            if command[1].startswith("@"):
                target_pseudo = command[1][1:]
                if target_pseudo in aliases:
                    query = f"SELECT login FROM Comptes WHERE pseudo='{target_pseudo}'"
                    cursor.execute(query)
                    result = cursor.fetchall()
                    target_login = result[0][0]
                    if target_login in accounts:
                        query = f"SELECT id_compte FROM Comptes WHERE login='{target_login}'"
                        cursor.execute(query)
                        result = cursor.fetchall()
                        id_compte = result[0][0]
                        query = f"DELETE FROM Sanctions WHERE compte='{id_compte}'"
                        cursor.execute(query)
                        connection.commit()
                        sanction_ban.append(target_login)
                        for k, v in client_conn.items():
                            if v == target_login:
                                k.send("server disconnection".encode())
                        reply = f"/!\ Le ban permanent de l'utilisateur {target_pseudo} a été annulé"
                        conn.send(reply.encode())
                    elif target_login not in accounts:
                        reply = f"/!\ L'utilisateur {target_pseudo} n'est pas sous l'effet d'un ban"
                        conn.send(reply.encode())
                elif target_pseudo in account_IP.values():
                    target_IP = target_pseudo
                    query = "SELECT IP FROM Sanctions WHERE type='ban'"
                    cursor.execute(query)
                    result = cursor.fetchall()
                    IP_kick = result[0][0]
                    if target_IP in IP_kick:
                        query = f"DELETE FROM Sanctions WHERE IP='{target_IP}'"
                        cursor.execute(query)
                        connection.commit()
                        reply = f"/!\ Le ban de l'adresse {target_IP} a été annulé"
                        conn.send(reply.encode())
                    elif target_IP not in IP_kick:
                        reply = f"/!\ L'adresse {target_IP} n'est pas sous l'effet d'un ban"
                        conn.send(reply.encode())
        elif msg.startswith("/unban") and client_conn[conn] not in superusers:
            reply = "Vous n'êtes pas autorisé à utiliser la commande /unban"
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

                        query = f"SELECT id_salon FROM Salon WHERE nom_salon='{salon}'"
                        cursor.execute(query)
                        result = cursor.fetchall()
                        id_salon = result[0][0]

                        query = f"UPDATE Comptes SET salon={id_salon} WHERE login='{login}'"
                        cursor.execute(query)
                        connection.commit()

                        reply = f"Déplacement dans le salon {salon}"
                        conn.send(reply.encode())
            elif len(command) == 3:
                if command[1].startswith("salon_") and command[2].startswith("@"):
                    target_pseudo = command[2][1:]
                    for k, v in aliases.items():
                        if v == target_pseudo:
                            target_login = k
                    if target_pseudo == admin_salon["Blabla"]:
                        query = f"SELECT id_compte FROM Comptes WHERE login='{login}'"
                        cursor.execute(query)
                        result = cursor.fetchall()
                        id_compte = result[0][0]

                        query = "INSERT INTO Autorisations (compte, salon, niv_auto) VALUES (%s, %s, %s)"
                        cursor.execute(query, (id_compte, 2, 1))
                        connection.commit()

                        reply = "Accès au salon 'Blabla' accordé"
                        conn.send(reply.encode())
                    elif target_pseudo == aliases[admin_salon[command[1][6:]]]:
                        query = f"SELECT id_compte FROM Comptes WHERE pseudo='{target_pseudo}'"
                        cursor.execute(query)
                        result = cursor.fetchall()
                        admin = result[0][0]

                        query = f"SELECT id_salon FROM Salon WHERE nom_salon='{command[1][6:]}'"
                        cursor.execute(query)
                        result = cursor.fetchall()
                        salon = result[0][0]

                        query = f"SELECT id_compte FROM Comptes WHERE pseudo='{pseudo}'"
                        cursor.execute(query)
                        result = cursor.fetchall()
                        compte = result[0][0]

                        query = "INSERT INTO Requetes (compte, admin, salon) VALUES (%s, %s, %s)"
                        cursor.execute(query, (compte, admin, salon))
                        connection.commit()

                        reply = f"Une requête à été faite auprès de {target_pseudo} pour accéder au salon {command[1][6:]}"
                        conn.send(reply.encode())
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
                            query = f"SELECT id_compte FROM Comptes WHERE login='{user_login}'"
                            cursor.execute(query)
                            result = cursor.fetchall()
                            id_compte = result[0][0]

                            query = f"SELECT id_salon FROM Salon WHERE nom_salon='{indiv_salon}'"
                            cursor.execute(query)
                            result = cursor.fetchall()
                            id_salon = result[0][0]

                            query = "INSERT INTO Autorisations (compte, salon, niv_auto) VALUES (%s, %s, %s)"
                            cursor.execute(query, (id_compte, id_salon, 1))
                            connection.commit()

                            query = f"DELETE FROM Requetes WHERE compte='{id_compte}'"
                            cursor.execute(query)
                            connection.commit()
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
                            query = f"SELECT id_compte FROM Comptes WHERE login='{user_login}'"
                            cursor.execute(query)
                            result = cursor.fetchall()
                            id_compte = result[0][0]

                            query = f"DELETE FROM Requetes WHERE compte='{id_compte}'"
                            cursor.execute(query)
                            connection.commit()
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
                    register_msg(msg, login, salon)          
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