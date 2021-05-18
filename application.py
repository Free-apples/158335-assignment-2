from flask import Flask, render_template
from flask_table import Table, Col, DatetimeCol
from boto3.dynamodb.conditions import Key, Attr
import boto3
import datetime
from flask_bootstrap import Bootstrap
import logging
from flask import *

application = Flask(__name__)
bootstrap = Bootstrap(application)

application.add_url_rule('/', 'index', (lambda: root()))
application.add_url_rule('/farmView', 'farmView', (lambda: farmView()))


def root():
    return render_template("index.html")


def farmView():
    #todo adjust this to work with login information
    farmId = 1
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    moistureLevelsTable = dynamodb.Table('MoistureLevels')
    waterRestrictionTable = dynamodb.Table('WaterRestriction')
    data = moistureLevelsTable.scan()
    tableItems = []
    items = []
    for i in data["Items"]:
        items.append(i)
    for key in items:
        tablefarmId = int(key["Farm-ID"])
        fieldId = int(key["Field-ID"])
        fieldMoist = bool(key["Field-moist"])
        tableItems.append(Item(tablefarmId, fieldId, fieldMoist))
    moistureLevelsTable = ItemTable(tableItems, classes=["table"])
    waterRestrictionsData = waterRestrictionTable.scan()
    rItems = []
    for i in waterRestrictionsData["Items"]:
        rItems.append(i)
    for key in rItems:
        if farmId == key["FarmId"]:
            restriction = "Farm ID is: " + str(farmId) + "Today's restriction is: " + str(int(key["Restriction"])) + "%"
            return render_template("farmView.html", table=moistureLevelsTable, restriction=restriction)
        else:
            return render_template("farmView.html", restriction="No data to show")



# Declare  table
class ItemTable(Table):
    farmId = Col("Farm Id")
    fieldId = Col("Field ID")
    fieldMoist = Col("Field Moist")

    def get_tr_attrs(self, item):
        status = item.status()
        return {'class': status}


# Get some objects
class Item(object):
    def __init__(self, farmId, fieldId, fieldMoist):
        self.farmId = farmId
        self.fieldId = fieldId
        self.fieldMoist = fieldMoist

    def status(self):
        if self.fieldMoist == False:
            return "table-danger"
        else:
            return "table-success"


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.secret_key = "abc"
    application.config['SESSION_TYPE'] = 'filesystem'
    application.debug = True
    application.run()


