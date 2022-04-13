import socket
import time

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((input("Host: "), int(input("Port: "))))
    #sock.setblocking(False)
    sock.send(b"Some stuff")
    sock.send(b"Some more stuff")
    
    print(sock.recv(1024))

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
