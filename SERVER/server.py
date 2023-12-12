import socket
import threading
import time

def connection(host, port, server_socket):
    global active
    global clients

    active = True
    clients = []
    client_threads = []

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

    flag = True
    flag_all = True

    while flag != False and flag_all != False:
        msg = conn.recv(1024).decode()
        print(f"message from {addr} is : {msg}")
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
        else:
            for client in clients:
                if client != conn:
                    client.send(f"message from {addr} is : {msg}".encode())

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