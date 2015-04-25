class Outerline(object):
    def __init__(self, w, lineNo):
        self.lineNo = lineNo
        self.status = True
        self.occupied = False
        self.window = w
        self.train = None
        if self.lineNo<6:
            self.body = self.window.create_rectangle(100, 250 + self.lineNo*50,
            300, 250+self.lineNo*50+10, fill="#080")
        else:
            self.body = self.window.create_rectangle(900, 250 + (self.lineNo-5)*50,
            1100, 250+(self.lineNo-5)*50+10, fill="#080")

    def update(self, w):
        self.window = w
        if self.occupied:
            self.window.itemconfigure(self.body, fill="#ff0000")
        else:
            self.window.itemconfigure(self.body, fill="#080")

