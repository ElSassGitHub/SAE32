import socket
import threading
import time

def send(client_socket):
    """
    Fonction utilisée par la thread gérant l'envoie de messages depuis le client
    
    :param client_socket: objet contenant les détails de la connection avec le serveur
    """
        
    global flag_snd
    flag_snd = True
    cursor_up = "\033[1A"
    clear = "\x1b[2K"

    try:
        while flag_snd != False:
            time.sleep(0.5)
            msg = input("Entrez le message à envoyer: ")
            if msg != "":
                client_socket.send(msg.encode())
            print(cursor_up + clear, end="")
    except OSError:
        print("La connection avec le serveur a été interrompue")

def receive(client_socket):
    """
    Fonction utilisée par la thread gérant la réception des messages venant du serveur
    
    :param client_socket: objet contenant les détails de la connection avec le serveur
    """

    global flag_snd

    flag_rcv = True

    cursor_up = "\033[1A"
    clear = "\x1b[2K"

    while flag_rcv != False:
        reply = client_socket.recv(1024).decode()
        print("\n" + cursor_up + clear, end="")
        if reply == "server disconnection":
            print(f"{reply}\n")
            flag_rcv = False
            flag_snd = False
            client_socket.close()
        elif reply.startswith("|") and reply.endswith("|"):
            salons = reply[2:-2]
            list_salons = salons.split(", ")
            print("Les salons disponibles sont: ")
            for salon in list_salons:
                option_salon = salon.replace("'", "")
                print(f"-> {option_salon}")
            print("\n")
        elif reply != "":
            print(f"{reply}\n")

def connection(client_socket):
    """
    Fonction gérant la connection à un compte (nouveau ou existant) sur le serveur de messagerie
    
    :param client_socket: objet contenant les détails de la connection avec le serveur
    """

    reply = ""
    account = False

    while account != True:
        question = client_socket.recv(1024).decode()
        if question == "account_exist":
            answer = input("Voulez-vous utiliser un compte déjà existant (yes/no) ? ")
            client_socket.send(answer.encode())
            next_step = client_socket.recv(1024).decode()
            if next_step == "initiate":
                while reply != "account_validated":
                    reply = client_socket.recv(1024).decode()
                    if reply == "serveur_login":
                        login = input("Quel est votre login ? ")
                        client_socket.send(login.encode())
                    elif reply == "serveur_password":
                        password = input("Quel est votre mot de passe ? ")
                        client_socket.send(password.encode())
                    elif reply == "account_pseudo":
                        pseudo = input("Quel est votre pseudo ? ")
                        client_socket.send(pseudo.encode())
                    elif reply == "recv_pseudo":
                        pseudo = client_socket.recv(1024).decode()
                    elif reply == "erroneous_account":
                        print("Le login et le mot de passe sont incorrects. \n")
                    elif reply == "pseudo_used":
                        print("Le pseudo est déjà utilisé par un autre utilisateur. \n")
                    elif reply == "account_validated":
                        account = True
            elif next_step == "account_restart":
                pass

    print(f"\nBienvenue sur le serveur Elsass_Chat, {pseudo} !\n")

def main():
    """
    fonction initialisant la connection avec le serveur de messagerie
    """

    host = str(input("Entrez l'adresse IP du serveur [127.0.0.1]: "))
    if host == "":
        host = "127.0.0.1"
    port = input("Entrez le port de connection au serveur [10000]: ")
    if port == "":
        port = 10000
    else:
        port = int(port)

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