import socketserver

PORT = 4206

class Handler(socketserver.BaseRequestHandler):

    def handle(self):
        while True:
            data = self.request.recv(1024)
            if not data:
                break
            print(data)
            self.request.send(bytes(reversed(data)))
        print("Done processing request")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as server:
        print("Serving on port", PORT)
        server.serve_forever()
