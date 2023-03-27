import datetime

class FpsCounter():
    def __init__(self):
        self.frames = 0
        self.t0 = False
    
    def start(self):
        if (self.t0 == False):
            self.t0 = datetime.datetime.now()

    def addFrame(self):
        self.frames += 1

    def getFps(self):
        elapsed_seconds = ( datetime.datetime.now() - self.t0).total_seconds()
        return self.frames / elapsed_seconds