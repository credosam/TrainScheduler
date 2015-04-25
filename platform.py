class Platform(object):
    def __init__(self, w, platformNo):
        self.platformNo = platformNo
        self.status = True
        self.occupied = False
        self.train = None
        self.x = 300
        self.window = w
        if self.platformNo%2==0:
            self.body = self.window.create_rectangle(350, 250 + 35*self.platformNo, 850,
                                250+35*self.platformNo+15, fill="#0000cc")
            self.trainy = 250 + 35*self.platformNo-10
        else:
            self.body = self.window.create_rectangle(350, 250+35*(self.platformNo)-20, 850,
                                250+35*(self.platformNo)-5, fill="#0000cc")
            self.trainy = 250+35*(self.platformNo)-20
