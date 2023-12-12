import socket
import threading
import time

def send(client_socket):
    global flag_snd
    flag_snd = True

    try:
        while flag_snd != False:
            time.sleep(0.5)
            msg = input("Entrez le message à envoyer: ")
            if msg != "":
                client_socket.send(msg.encode())
    except OSError:
        print("La connection avec le serveur a été interrompue")

def receive(client_socket):
    global flag_snd

    flag_rcv = True

    while flag_rcv != False:
        reply = client_socket.recv(1024).decode()
        print(f"\n{reply}")
        if reply == "server disconnection":
            flag_rcv = False
            flag_snd = False
            client_socket.close()

def connection(client_socket):
    reply = ""

    while reply != "pseudo_validated":
        reply = client_socket.recv(1024).decode()
        if reply == "serveur_pseudo":
            pseudo = input("Quel est votre pseudo ? ")
            client_socket.send(pseudo.encode())
        elif reply == "pseudo_not_allowed":
            pseudo = input("Pseudo déjà utilisé. Merci d'en choisir un autre : ")
            client_socket.send(pseudo.encode())

def main():
    host = '127.0.0.1'
    port = 10000

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    connection(client_socket)
    rcv_thread = threading.Thread(target=receive, args=[client_socket])
    send_thread = threading.Thread(target=send, args=[client_socket])
    
    send_thread.start()
    rcv_thread.start()

    send_thread.join()
    rcv_thread.join()

if __name__ == '__main__':
    main()