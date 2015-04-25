from Tkinter import *
from train import *
from platform import *
from outerline import *
from db import *
from dialogs import *
import time

startingTime = 0
leavingTime = 0
delay = 0
trainsOnPlatform = []       
waitingtrains = []  
trainsOnOuterlines = []    
allTrains = []         
allPlatforms = []      
allOuterlines = []         
startstate = False
fps = 100/6
counter = 11.9*60*60
timecount = ''
mx = len(list(getTrainList().find()))
tablegrid = []

def timetoint(depttime):
	[hour, mint] = depttime.split(':')
	time = 0
	time += int(hour)*60
	time += int(mint)
	return time

class App:

    def __init__(self, master):
        global w, allTrains, allPlatforms, allOuterlines, table


        self.f = Frame(master, width=1300, height=300)
        self.f.pack(side=TOP)
        # self.f.configure(bg = "#333333")

        self.w = Canvas(master, width=1300, height=900)
        self.w.pack(side=BOTTOM)
        self.w.configure(bg = "#333333")

        for platform in getPlatformList().find():
            plat = Platform(self.w, platform['number'])
            if platform['status']=='DISABLED':
                plat.status = False
            allPlatforms.append(plat)

        for i in range(10):
            allOuterlines.append(Outerline(self.w, i+1))

        self.createButtons(self.f)

    def createButtons(self, arena):
        self.stsim = Button(arena, text="Start Simulation", command=self.startsimulate)
        self.stsim.pack(side=LEFT)
        
        self.stosim = Button(arena, text="Stop Simulation", command=self.stopsimulate, state=DISABLED)
        self.stosim.pack(side=LEFT)
        
        self.addTrain = Button(arena, text="Add Train", command=lambda: self.addTrainClicked(master))
        self.addTrain.pack(side=LEFT)

        self.deleteTrain = Button(arena, text="Delete Train", command=lambda: self.deleteTrainClicked(master))
        self.deleteTrain.pack(side=LEFT)

        self.editTrain = Button(arena, text="Edit Train", command=lambda: self.editTrainClicked(master))
        self.editTrain.pack(side=LEFT)

        self.addPlatform = Button(arena, text="Add Platform", command=lambda: self.addPlatformClicked(master))
        self.addPlatform.pack(side=LEFT)

        self.editPlatform = Button(arena, text="Edit Platform", command=lambda: self.editPlatformClicked(master))
        self.editPlatform.pack(side=LEFT)

        self.quit = Button(arena, text="Exit", fg="red", command=arena.quit)
        self.quit.pack(side=LEFT)


    def startsimulate(self):
        global startstate
        startstate = True
        counter_label(timer)
        master.after(10, simulate)
        self.stsim.config(state=DISABLED)
        self.stosim.config(state=NORMAL)
        updateData()
    
    def stopsimulate(self):
        global startstate, startingTime, leavingTime
        startstate = False
        self.stsim.config(state=NORMAL)
        self.stosim.config(state=DISABLED)
        for train in allTrains:
        	leavingTime += timetoint(train.departure)
        delay = leavingTime - startingTime
        print delay

    def addTrainClicked(self,master):
        dialog = addTrainDialog(master)
        master.wait_window(dialog.top)

    def deleteTrainClicked(self,master):
        dialog = deleteTrainDialog(master)
        master.wait_window(dialog.top)

    def editTrainClicked(self,master):
        dialog = editTrainDialog(master)
        master.wait_window(dialog.top)

    def addPlatformClicked(self,master):
        dialog = addPlatformDialog(master)
        master.wait_window(dialog.top)

    def editPlatformClicked(self,master):
        dialog = editPlatformDialog(master)
        master.wait_window(dialog.top)

def schedule():
    global waitingtrains, trainsOnPlatform, trainsOnOuterlines, startingTime

    for train in getTrainList().find().sort([('arrival_time',pymongo.ASCENDING)]):
        departureTime = departureTimeFind(train['arrival_time'], train['type'])
        currentTrain = Train(app.w, train['code'], train['name'], train['arrival_time'], departureTime, train['type'])
        allTrains.append(currentTrain)
        waitingtrains.append(currentTrain)
        startingTime += timetoint(departureTime)

def departureTimeFind(arrival, category):
    [hour, mint] = arrival.split(':')
    if category=="Passing":
        if int(mint)>=55:
            hour = str((int(hour)+1)%24)
        mint=str((int(mint)+5)%60)
    else:
        if int(mint)>=45:
            hour = str((int(hour)+1)%24)
        mint=str((int(mint)+15)%60)
    if len(hour)<2:
        hour = '0'+hour
    if len(mint)<2:
        mint = '0'+mint
    return hour+':'+mint


def simulate():
    global startstate, trainsOnPlatform, trainsOnOuterlines, waitingtrains
    global allTrains, allPlatforms, allOuterlines
    for trains in trainsOnPlatform:
        if timecount>=trains.departure:
            trains.vel = 3
            trains.platform = 0
            trains.status = "departed"
            updateData()
            for p in allPlatforms:
                if p.train==trains and trains.x>=400:
                    p.train = None
                    p.occupied = False
                    del trainsOnPlatform[trainsOnPlatform.index(trains)]
                    break

    for trains in trainsOnOuterlines:
        flag = 0
        for p in allPlatforms:
            if not p.occupied and p.status:
                flag = 1
                outer = trains.outerline
                trains.vel = 3
                app.w.move(trains.body, 0, p.trainy-trains.y)
                app.w.move(trains.label, 0, p.trainy-trains.y)
                trains.platform = p.platformNo
                trains.status = "arrived"
                trains.departure = departureTimeFind(timecount, trains.category)
                p.occupied = True
                p.train = trains
                del trainsOnOuterlines[trainsOnOuterlines.index(trains)]
                updateData()
                trainsOnPlatform.append(trains)
                for outerline in allOuterlines:
                    if outerline.train==trains:
                        outerline.train = None
                        outerline.occupied = False
                        break
                break
        if flag==0:
            break

    for train in waitingtrains:
        flag = 0
        if timecount>=train.arrival:
            for p in allPlatforms:
                if (not p.occupied) and p.status:
                    flag = 1
                    train.vel = 3
                    train.platform = p.platformNo
                    app.w.move(train.body, 0, p.trainy-train.y)
                    app.w.move(train.label, 0, p.trainy-train.y)
                    train.status = "arrived"
                    train.departure = departureTimeFind(timecount, train.category)
                    p.occupied = True
                    p.train = train
                    del waitingtrains[waitingtrains.index(train)]
                    updateData()
                    trainsOnPlatform.append(train)
                    break
            if flag==0:
                for outerline in allOuterlines:
                    if not outerline.occupied:
                        outerline.occupied = True
                        outerline.train = train
                        del waitingtrains[waitingtrains.index(train)]
                        trainsOnOuterlines.append(train)
                        outerline.update(app.w)
                        break
                break

    for train in allTrains:
        if (train.x<400 and train.status=='arrived') or train.status=='departed':
            train.update(app.w)
    for outerline in allOuterlines:
        outerline.update(app.w)

    if startstate:
        master.after(5, simulate)

def counter_label(label):
    def count():
        global counter, startstate, timecount
        counter += 1
        timecount = time.strftime("%H:%M", time.gmtime(counter))
        label.config(text="Time: "+time.strftime("%H:%M", time.gmtime(counter)))
        if(startstate):
            label.after(fps, count)
    count()

def data():
    global tablegrid
    Label(frame).grid(row=0,column=0,padx=100)
    currow = []
    label = Label(frame, text="Train Code",font = "Helvetica 14 bold")
    label.grid(row=0,column=4,padx=30)
    currow.append(label)
    label = Label(frame,text="Train Name",font = "Helvetica 14 bold")
    label.grid(row=0,column=8,padx=30)
    currow.append(label)
    label = Label(frame,text="Arrival Time",font = "Helvetica 14 bold")
    label.grid(row=0,column=12,padx=30)
    currow.append(label)
    label = Label(frame,text="Departure Time",font = "Helvetica 14 bold")
    label.grid(row=0,column=16,padx=30)
    currow.append(label)
    label = Label(frame,text="Platform Number",font = "Helvetica 14 bold")
    label.grid(row=0,column=20,padx=30)
    currow.append(label)
    tablegrid.append(currow)
    i = 0
    for trains in waitingtrains:
        currow = []
        label = Label(frame,text=trains.code,font = "Helvetica 10")
        label.grid(row=i+1,column=4)
        currow.append(label)
        label = Label(frame,text=trains.name,font = "Helvetica 10")
        label.grid(row=i+1,column=8)
        currow.append(label)
        label = Label(frame,text=trains.arrival,font = "Helvetica 10")
        label.grid(row=i+1,column=12)
        currow.append(label)
        label = Label(frame,text=trains.departure,font = "Helvetica 10")
        label.grid(row=i+1,column=16)
        currow.append(label)
        label = Label(frame,text=trains.platform,font = "Helvetica 10")
        label.grid(row=i+1,column=20)
        currow.append(label)
        tablegrid.append(currow)
        i+=1

def updateData():
    global tablegrid
    i = 1
    for t in allTrains:
        tablegrid[i][0].configure(text=t.code)
        tablegrid[i][1].configure(text=t.name)
        tablegrid[i][2].configure(text=t.arrival)
        tablegrid[i][3].configure(text=t.departure)
        if str(t.platform)=='0':
            tablegrid[i][4].configure(text='---')
        else:
            tablegrid[i][4].configure(text=t.platform)
        i = i+1


def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"),width=master.winfo_screenwidth()-100,height=200)



class addTrainDialog:

    def __init__(self, parent):


        self.top = Toplevel(parent)

        Label(self.top, text="Train Number").grid(row=0, column=0)
        self.trainNumberEntered = StringVar(self.top)
        self.trainNumber = Entry(self.top, textvariable=self.trainNumberEntered).grid(row=0, column=1)


        Label(self.top, text="Train Name").grid(row=1, column=0)
        self.trainNameEntered = StringVar(self.top)
        self.trainName = Entry(self.top, textvariable=self.trainNameEntered).grid(row=1, column=1)

        Label(self.top, text="Arrival Time").grid(row=2, column=0)
        self.arrivalTimeEntered = StringVar(self.top)
        self.arrivalTimeEntered.set("00:00")
        self.arrivalTime = Entry(self.top, textvariable=self.arrivalTimeEntered).grid(row=2, column=1)

        self.trainTypeOptions = ["Originating","Destination","Passing"]
        self.trainTypeSelected = StringVar(self.top)
        self.trainTypeSelected.set(self.trainTypeOptions[0])
        Label(self.top, text="Train Type").grid(row=3, column=0)
        self.trainType = OptionMenu(self.top, self.trainTypeSelected, *self.trainTypeOptions).grid(row=3, column=1)

        self.trainDirectionOptions = ["<NA>","West","East"]
        self.trainFromDirectionSelected = StringVar(self.top)
        self.trainFromDirectionSelected.set(self.trainDirectionOptions[0])
        self.trainToDirectionSelected = StringVar(self.top)
        self.trainToDirectionSelected.set(self.trainDirectionOptions[0])
        Label(self.top, text="From Direction").grid(row=4, column=0)
        Label(self.top, text="To Direction").grid(row=5, column=0)
        self.trainType = OptionMenu(self.top, self.trainFromDirectionSelected, *self.trainDirectionOptions).grid(row=4, column=1)
        self.trainType = OptionMenu(self.top, self.trainToDirectionSelected, *self.trainDirectionOptions).grid(row=5, column=1)

        self.submitButton = Button(self.top, text="Submit", command=self.submit).grid(row=6, column=0)
        self.cancelButton = Button(self.top, text="Cancel", command=self.cancel).grid(row=6, column=1)

    def submit(self):

        trainCode = self.trainNumberEntered.get()
        trainName = self.trainNameEntered.get()
        trainTime = self.arrivalTimeEntered.get()
        trainType = self.trainTypeSelected.get()
        trainDirection = self.trainFromDirectionSelected.get()

        addTrain(trainName, trainCode, trainTime, trainDirection, "NOT_ARRIVED", trainType)

        departureTime = finddep(trainTime, trainType)
        tr = Train(app.w, trainCode, trainName, trainTime, departureTime, trainType)
        allTrains.append(tr)
        waitingtrains.append(tr)
        waitingtrains.sort(key=lambda x: x.arrival)
        allTrains.sort(key=lambda x: x.arrival)

        currow = []
        i = len(allTrains)
        label = Label(frame,text=trainCode,font = "Helvetica 10")
        label.grid(row=i,column=4)
        currow.append(label)
        label = Label(frame,text=trainName,font = "Helvetica 10")
        label.grid(row=i,column=8)
        currow.append(label)
        label = Label(frame,text=trainTime,font = "Helvetica 10")
        label.grid(row=i,column=12)
        currow.append(label)
        label = Label(frame,text=departureTime,font = "Helvetica 10")
        label.grid(row=i,column=16)
        currow.append(label)
        label = Label(frame,text='0',font = "Helvetica 10")
        label.grid(row=i,column=20)
        currow.append(label)
        tablegrid.append(currow)

        updateData()

        self.top.destroy()

    def cancel(self):
        self.top.destroy()


class deleteTrainDialog:

    def __init__(self,parent):

        self.top = Toplevel(parent)

        Label(self.top, text="Train Number").grid(row=0, column=0)
        self.trainNumberSelected = StringVar(self.top)

        self.trainNumberOptions = []
        for train in getTrainList().find():
            self.trainNumberOptions.append(train["code"])

        self.trainNumberSelected.set(self.trainNumberOptions[0])
        self.trainNumber = OptionMenu(self.top, self.trainNumberSelected, *self.trainNumberOptions).grid(row=0, column=1)

        self.submitButton = Button(self.top, text="Submit", command=self.submit).grid(row=1, column=0)
        self.cancelButton = Button(self.top, text="Cancel", command=self.cancel).grid(row=1, column=1)

    def submit(self):

        trainCode = self.trainNumberSelected.get()
        deleteTrain(trainCode)

        for t in allTrains:
            if t.code==trainCode:
                del allTrains[allTrains.index(t)]
                break
        for row in tablegrid:
            if row[0].cget("text")==trainCode:
                for label in row:
                    label.destroy()
                break

        updateData()

        self.top.destroy()

    def cancel(self):

        self.top.destroy()


class editTrainDialog:

    def __init__(self,parent):

        self.top = Toplevel(parent)

        Label(self.top, text="Train Number").grid(row=0, column=0)
        self.trainNumberSelected = StringVar(self.top)

        self.trainNumberOptions = []
        for train in getTrainList().find():
            self.trainNumberOptions.append(train["code"])

        self.trainNumber = OptionMenu(self.top, self.trainNumberSelected, *self.trainNumberOptions).grid(row=0, column=1)

        Label(self.top, text="Train Time").grid(row=1, column=0)
        self.arrivalTimeEntered = StringVar(self.top)
        self.arrivalTime = Entry(self.top, textvariable=self.arrivalTimeEntered).grid(row=1, column=1)

        self.submitButton = Button(self.top, text="Submit", command=self.submit).grid(row=2, column=0)
        self.cancelButton = Button(self.top, text="Cancel", command=self.cancel).grid(row=2, column=1)

        self.trainNumberSelected.trace('w', self.fillTrainTime)
        self.trainNumberSelected.set(self.trainNumberOptions[0])

    def fillTrainTime(self, *args):

        trainCode = self.trainNumberSelected.get()
        for train in getTrainList().find():
            if train["code"]==trainCode:
                self.arrivalTimeEntered.set(train["arrival_time"])
        

    def submit(self):

        trainCode = self.trainNumberSelected.get()
        trainTime = self.arrivalTimeEntered.get()
        updateTrainArrivalTime(trainCode, trainTime)

        for t in allTrains:
            if t.code==trainCode:
                t.arrival = trainTime
                t.departure = finddep(trainTime, t.category)
                break

        waitingtrains.sort(key=lambda x: x.arrival)
        allTrains.sort(key=lambda x: x.arrival)

        updateData()

        self.top.destroy()

    def cancel(self):

        self.top.destroy()


class addPlatformDialog:

    def __init__(self,parent):

        self.top = Toplevel(parent)

        Label(self.top, text="Number of platforms").grid(row=0, column=0)
        self.platformNumberEntered = StringVar(self.top)
        self.platformNumber = Entry(self.top, textvariable=self.platformNumberEntered).grid(row=0, column=1)

        self.submitButton = Button(self.top, text="Submit", command=self.submit).grid(row=1, column=0)
        self.cancelButton = Button(self.top, text="Cancel", command=self.cancel).grid(row=1, column=1)

    def submit(self):

        platformNumber = self.platformNumberEntered.get()

        platformCount = 0
        for platform in platforms.find():
            platformCount = platformCount + 1

        for i in range(1,int(platformNumber)+1):
            addPlatform(i+platformCount,"ENABLED","EMPTY","0")
            pl = Platform(app.w, i+platformCount)
            allPlatforms.append(pl)

        self.top.destroy()

    def cancel(self):

        self.top.destroy()


class editPlatformDialog:

    def __init__(self,parent):

        self.top = Toplevel(parent)

        platformCount = 0
        for platform in platforms.find():
            platformCount = platformCount + 1

        self.platformList = []
        self.platformStatus = []

        for i in range(0,platformCount):
            self.platformStatus.append(IntVar(self.top))
            self.platformStatus[i].set(1)
        
        for i in range(1,platformCount+1):
            Label(self.top, text=("Platform "+str(i))).grid(row=i-1,column=0)
            self.platformList.append(Checkbutton(self.top, variable=self.platformStatus[i-1]))
            self.platformList[i-1].grid(row=i-1, column=1)
            self.platformList[i-1].deselect()

        for platform in platforms.find():
            if platform["status"]=="DISABLED":
                self.platformList[int(platform["number"]-1)].select()

        self.submitButton = Button(self.top, text="Submit", command=self.submit).grid(row=platformCount, column=0)
        self.cancelButton = Button(self.top, text="Cancel", command=self.cancel).grid(row=platformCount, column=1)

    def submit(self):

        i=1
        for status in self.platformStatus:
            if status.get()==1:
                updatePlatformStatus(i,"DISABLED")
                for p in allPlatforms:
                    if p.platformNo==i:
                        p.status=False
                        break
            else:
                updatePlatformStatus(i,"ENABLED")
                for p in allPlatforms:
                    if p.platformNo==i:
                        p.status=True
                        break
            i=i+1


        self.top.destroy()

    def cancel(self):

        self.top.destroy()


master = Tk()

master.configure(bg = "#333333")
posx = 0
posy = 0
screenWidth = master.winfo_screenwidth()
screenHeight = master.winfo_screenheight()
master.wm_geometry("%dx%d+%d+%d" % (screenWidth, screenHeight, posx, posy))


timer = Label(master, fg="yellow", font = "Helvetica 18 bold")
timer.pack()
timer.configure(bg = "#333333")
app = App(master)

myframe=Frame(master,relief=GROOVE,width=50,height=100,bd=1)
myframe.place(x=15,y=master.winfo_screenheight()-680)
# myframe.configure(bg = "#333333")

canvas=Canvas(myframe)
frame=Frame(canvas)
myscrollbar=Scrollbar(myframe,orient="vertical",command=canvas.yview)
canvas.configure(yscrollcommand=myscrollbar.set)
# canvas.configure(bg = "#333333")

myscrollbar.pack(side="right",fill="y")
canvas.pack(side="top")
canvas.create_window((0,0),window=frame,anchor='nw')
frame.bind("<Configure>",myfunction)

schedule()
data()
master.mainloop()