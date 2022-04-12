import socket

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((input("Host: "), int(input("Port: "))))
    sock.send(input("Enter data: ").encode("ascii"))
    print(sock.recv(1024))
