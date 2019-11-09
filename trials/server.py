import queue
import threading
import socket

def run_sockets(connection_queue):


if __name__ == '__main__':
    connection_queue = queue.Queue()
    socket_runner = threading.Thread(target=

    s = socket.socket()
    s.bind(("localhost", 12345))
    s.listen(5)
    while True:
        print("Waiting for connection")
        client_socket, address = s.accept()
        print(client_socket.recv(100))

