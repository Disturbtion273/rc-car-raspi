import time

class Intersection:
    def __init__(self, driving, lineFollower, websocketServer):
        self.lineFollower = lineFollower
        self.direction = "center"
        self.driving = driving
        self.websocket = websocketServer
        self.isWaitedForWebsocketCommand = False

        self.maxSpeed = 0

    def SendIntersectionCommand(self):
        self.websocket.Send("intersection")

    def StartIntersection(self):
        self.driving.SetMaxSpeedPercent(0)
        self.isWaitedForWebsocketCommand = True
        self.SendIntersectionCommand()
        
    def SetIntersectionDirection(self, direction):
        if not self.isWaitedForWebsocketCommand:
            return
        if direction in ["left", "center", "right"]:
            self.direction = direction
            self.lineFollower.SetDirection(direction)
        else:
            raise ValueError("Invalid direction. Use 'left', 'center', or 'right'.")

        def continueCenterDriving():
            self.driving.SetMaxSpeedPercent(100)
            self.lineFollower.SetDirection("center")

        timer = threading.Timer(4.0, continueCenterDriving)
        timer.start()