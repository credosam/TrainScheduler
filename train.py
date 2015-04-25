class Train(object):
    """Name of the train along with his trainCode, Arrival Time Departure Time"""
    def __init__(self, w, code, name, arrival, departure, category, platform=0, outerline=0, status="notarrived"):
        self.name = name
        self.code = code
        self.platform = platform
        self.outerline = outerline
        self.status = status
        self.arrival = arrival
        self.departure = departure
        self.category = category
        self.vel = 0
        self.window = w
        self.body = self.window.create_rectangle(-400, 20, 0, 45, fill="#ffffff")
        self.x = self.window.coords(self.body)[0]
        self.y = self.window.coords(self.body)[1]
        self.label = self.window.create_text(self.x+175, self.y+7, text=str(self.name))

    def update(self, w):
        """ Called each frame. """
        self.window = w
        self.window.move(self.body, self.vel, 0)
        self.window.move(self.label, self.vel, 0)
        self.x = self.window.coords(self.body)[0]
        self.y = self.window.coords(self.body)[1]
        self.window.update()
