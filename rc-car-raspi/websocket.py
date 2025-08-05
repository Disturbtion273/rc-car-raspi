import threading
from queue import Queue

from websockets.sync.server import serve


class WebsocketServer:
    queue = Queue()

    @staticmethod
    def Start(host, port):
        threading.Thread(target=WebsocketServer.Serve, args=(host, port), daemon=True).start()

    @staticmethod
    def Serve(host, port):
        with serve(WebsocketServer.MessageHandler, host, port) as server:
            server.serve_forever()

    @staticmethod
    def MessageHandler(websocket):
        def Send():
            while True:
                if WebsocketServer.queue.empty():
                    continue
                queueItem = WebsocketServer.queue.get()
                websocket.send(queueItem)

        threading.Thread(target=Send, daemon=True).start()
        for message in websocket:
            print(message)
            ### Here you can handle the incoming message
            # handle_message(message) {
            #     drive(message["drive"])
            #     lenk(message["lenk"])
            # }

    @staticmethod
    def Send(message):
        WebsocketServer.queue.put(message)

if __name__ == "__main__":
    WebsocketServer.Start("0.0.0.0", 9999)
    while True:
        message = input("Enter message to send: ")
        WebsocketServer.Send(message)
        print(message)
