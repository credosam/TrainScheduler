class Sideline(object):
    def __init__(self, w, lineNo):
        self.lineNo = lineNo
        self.occupied = False
        self.status = True
        self.train = None
        if self.lineNo<6:
            self.body = w.create_rectangle(100, 250 + self.lineNo*50,
            300, 250+self.lineNo*50+8, fill="#080")
        else:
            self.body = w.create_rectangle(900, 250 + (self.lineNo-5)*50,
            1100, 250+(self.lineNo-5)*50+8, fill="#080")

    def update(self, w):
        if self.occupied:
            w.itemconfigure(self.body, fill="#ff0000")
        else:
            w.itemconfigure(self.body, fill="#080")