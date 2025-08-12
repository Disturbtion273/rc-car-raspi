import threading
from queue import Queue
from websockets.sync.server import serve

class WebsocketServer:
    def __init__(self, WebsocketCommandHandler):
        self.commandHandler = WebsocketCommandHandler
        self.queue = Queue()

    def Start(self, host, port):
        threading.Thread(target=self.Serve, args=(host, port), daemon=True).start()

    def Serve(self, host, port):
        with serve(self.MessageHandler, host, port) as server:
            server.serve_forever()

    def MessageHandler(self, websocket):
        def Send():
            while True:
                try:
                    queueItem = self.queue.get()
                    websocket.send(queueItem)
                except Exception as e:
                    print(f"Send-Error: {e}")
                    break  

        threading.Thread(target=Send, daemon=True).start()

        try:
            for message in websocket:
                print(f"Received message: {message}")
                self.commandHandler.handleMessage(message)
        except Exception as e:
            print(f"Receive-Error: {e}")

    def Send(self, message):
        self.queue.put(message)
