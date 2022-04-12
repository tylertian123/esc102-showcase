import socketserver

PORT = 4206

class Handler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        print(data)
        self.request.send(bytes(reversed(data)))

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as server:
        print("Serving on port", PORT)
        server.serve_forever()
