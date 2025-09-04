import threading
from queue import Queue
from websockets.sync.server import serve
from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK

class WebsocketServer:
    def __init__(self, WebsocketCommandHandler):
        self.commandHandler = WebsocketCommandHandler
        self.queue = Queue()

    def SetCommandHandler(self, handler):
        self.commandHandler = handler

    def Start(self, host, port):
        threading.Thread(target=self.Serve, args=(host, port), daemon=True).start()

    def Serve(self, host, port):
        with serve(self.MessageHandler, host, port) as server:
            server.serve_forever()

    def MessageHandler(self, websocket):
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        print(f"New client connected from {client_info}")

        def Send():
            while True:
                try:
                    queueItem = self.queue.get()
                    websocket.send(queueItem)
                except ConnectionClosedError as e:
                    print(f"Connection from {client_info} was closed abnormally: {e}")
                    break
                except ConnectionClosedOK as e:
                    print(f"Connection from {client_info} was closed normally: {e}")
                    break
                except Exception as e:
                    print(f"Send-Error for client {client_info}: {e}")
                    break

        threading.Thread(target=Send, daemon=True).start()

        try:
            for message in websocket:
                self.commandHandler.HandleMessage(message)
        except ConnectionClosedError as e:
            print(f"Connection from {client_info} was closed abnormally: {e}")
        except ConnectionClosedOK as e:
            print(f"Connection from {client_info} was closed normally: {e}")
        except Exception as e:
            print(f"Receive-Error from client {client_info}: {e}")
        finally:
            print(f"Client {client_info} disconnected")

    def Send(self, message):
        self.queue.put(message)

