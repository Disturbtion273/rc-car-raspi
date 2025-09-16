import time
import threading

class Intersection:
    isWaitedForWebsocketCommand = False
    def __init__(self, driving, lineFollower):
        self.lineFollower = lineFollower
        self.direction = "center"
        self.driving = driving
        Intersection.isWaitedForWebsocketCommand = False

        self.maxSpeed = 0

    def StartIntersection(self):
        self.driving.SetMaxSpeedPercent(0)
        Intersection.isWaitedForWebsocketCommand = True
        
    def SetIntersectionDirection(self, direction):
        if not Intersection.isWaitedForWebsocketCommand:
            return
        if direction in ["left", "center", "right"]:
            self.direction = direction
            self.lineFollower.SetDirection(direction)
            Intersection.isWaitedForWebsocketCommand = False
            self.driving.SetMaxSpeedPercent(100)
        else:
            raise ValueError("Invalid direction. Use 'left', 'center', or 'right'.")

        def continueCenterDriving():
            self.lineFollower.SetDirection("center")

        timer = threading.Timer(4.0, continueCenterDriving)
        timer.start()