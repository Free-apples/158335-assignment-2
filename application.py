from flask import Flask, render_template
from flask_table import Table, Col, DatetimeCol
from boto3.dynamodb.conditions import Key
import boto3
import datetime
from flask_bootstrap import Bootstrap
import logging


application = Flask(__name__)
bootstrap = Bootstrap(application)

# for i in range(len(data)):
#     print(i)
#     data = data['Items'][i]
#     timeStamp = int(data["sample_time"])
#     time = datetime.datetime.fromtimestamp(timeStamp / 1e3)
#     device_data = data["device_data"]
#     deviceId = data["device_id"]
#     waterLevel = device_data["waterLevel"]
#     toiletPaperLevel = device_data["toiletPaperLevel"]
#     usage = device_data["usage"]
#     items.append(Item(time, deviceId, waterLevel, toiletPaperLevel, usage))
# table = ItemTable(items, classes=["table"])
# return render_template("index.html", table=table)

def root():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('portaloo_data')
    data = table.scan()
    tableItems = []
    items = []
    for i in data["Items"]:
        items.append(i)
    for key in items:
        timeStamp = int(key["sample_time"])
        time = datetime.datetime.fromtimestamp(timeStamp / 1e3)
        device_data = key["device_data"]
        deviceId = int(key["device_id"])
        waterLevel = device_data["waterLevel"]
        toiletPaperLevel = device_data["toiletPaperLevel"]
        usage = device_data["usage"]
        tableItems.append(Item(time, deviceId, waterLevel, toiletPaperLevel, usage))
    table = ItemTable(tableItems, classes=["table"])
    return render_template("index.html", table=table)



application.add_url_rule('/', 'index', (lambda : root()))
# Declare your table
class ItemTable(Table):
    time = DatetimeCol('Time')
    deviceID = Col('Device ID')
    waterLevel = Col('Water level')
    toiletPaperLevel = Col("Toilet Paper Level")
    usage = Col("Usage")

    def get_tr_attrs(self, item):
        status = item.status()
        return {'class': status}



# Get some objects
class Item(object):
    def __init__(self, time, deviceID, waterLevel, toiletPaperLevel, usage):
        self.time = time
        self.deviceID = deviceID
        self.waterLevel = waterLevel
        self.toiletPaperLevel = toiletPaperLevel
        self.usage = usage

    def status(self):
        if self.waterLevel <= 10 or self.toiletPaperLevel <= 10 or self.usage >= 100:
            return "table-danger"
        elif self.waterLevel >= 30 or self.toiletPaperLevel >= 30 or self.usage <= 20:
            return "table-success"
        else:
            return "table-warning"



# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
