from flask import Flask, render_template
from flask_table import Table, Col, DatetimeCol
from boto3.dynamodb.conditions import Key, Attr
import boto3
import datetime
from flask_bootstrap import Bootstrap
import logging


application = Flask(__name__)
bootstrap = Bootstrap(application)


def root():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('portalooDataRecent')
    data = table.scan()
    #dictOfinput = {}
    #data = table.query(KeyConditionExpression=Key('sample_time').eq('latest_entry_identifier'))
    tableItems = []
    items = []
    for i in data["Items"]:
        items.append(i)
    for key in items:
        #timeStamp = int(key["sample_time"])
        #time = datetime.datetime.fromtimestamp(timeStamp / 1e3)
        device_data = key["device_data"]
        deviceId = int(key["device_id"])
        #if deviceId not in dictOfinput or dictOfinput[deviceId] < time:
        #    dictOfinput[deviceId] = time
        waterLevel = device_data["waterLevel"]
        toiletPaperLevel = device_data["toiletPaperLevel"]
        usage = device_data["usage"]
        humidity = device_data["humidity"]
        temperature = device_data["temperature"]
        orientation = device_data["orientation"]
        sampleTime = device_data["sampleTime"]
        tableItems.append(Item(deviceId, waterLevel, toiletPaperLevel, usage, humidity, temperature, orientation, sampleTime))
    table = ItemTable(tableItems, classes=["table"])

    return render_template("index.html", table=table)



application.add_url_rule('/', 'index', (lambda : root()))
# Declare your table
class ItemTable(Table):
    # todo fix why time is not working correctly
    deviceID = Col('Portaloo ID')
    waterLevel = Col('Water level')
    toiletPaperLevel = Col("Toilet Paper Level")
    usage = Col("Usage since last service")
    humidity = Col("Current humidity")
    temperature = Col("Current temperature")
    orientation = Col("Upright?")
    sampleTime = Col("Sample Time")

    def get_tr_attrs(self, item):
        status = item.status()
        return {'class': status}


# Get some objects
class Item(object):
    def __init__(self, deviceID, waterLevel, toiletPaperLevel, usage, humidity, temperature, orientation, sampleTime):
        self.deviceID = deviceID
        self.waterLevel = waterLevel
        self.toiletPaperLevel = toiletPaperLevel
        self.usage = usage
        self.humidity = humidity
        self.temperature = temperature
        self.orientation = orientation
        self.sampleTime = sampleTime

    def status(self):
        if self.waterLevel <= 10 or self.toiletPaperLevel <= 10 or self.usage >= 100 or self.orientation == False:
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
