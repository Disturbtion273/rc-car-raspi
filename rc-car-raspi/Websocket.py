import threading
import asyncio
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
                if self.queue.empty():
                    continue
                queueItem = self.queue.get()
                websocket.send(queueItem)

        threading.Thread(target=Send, daemon=True).start()
        for message in websocket:
            print(f"Received message: {message}")
            self.commandHandler.handleMessage(message)

    def Send(self, message):
        self.queue.put(message)