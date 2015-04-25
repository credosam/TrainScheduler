import pymongo

# Connection to Mongo DB
try:
    conn=pymongo.MongoClient()
    print "Connected successfully"
except pymongo.errors.ConnectionFailure, e:
    print "Could not connect to MongoDB: %s" % e
    
db = conn.mydb
db = conn['station']
trains = db.train
platforms = db.platform
outer_lines = db.outer_lines

def addTrain(name,code,arrival_time,direction,status,type):
    train = {"name":name,"code":code,"arrival_time":arrival_time,"direction":direction,"status":status,"type":type}
    trains.insert(train)
    print "success"

def getTrainList():
    return trains

def deleteTrain(code):
    trains.remove({"code":code})

def getTrain(code):
    return trains.find({"code":code})

def updateTrainArrivalTime(code,time):
    trains.update({"code":code},{'$set':{"arrival_time":time}})

def addPlatform(number,status,occupancy,code):
    platform = {"number":number,"status":status,"occupancy":occupancy,"code":code}
    platforms.insert(platform)

def getPlatformList():
    return platforms

def updatePlatformStatus(number,status):
    platforms.update({"number":number},{'$set':{"status":status}})

def updatePlatformOccupancy(number,occupancy):
    platforms.update({"number":number},{'$set':{"occupancy":occupancy}})

def addOuterLines(number,occupancy,code):
    outer_line = {"number":number,"occupancy":occupancy,"code":code}
    outer_lines.insert(outer_line)

def updateOuterLines(number,occupancy):
    outer_lines.update({"number":number},{'$set':{"occupancy":occupancy}})

def getOuterLineList():
    return outer_lines
