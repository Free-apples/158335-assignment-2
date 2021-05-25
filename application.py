from flask import Flask, render_template, request, redirect, make_response, jsonify, url_for, session
from flask_awscognito import AWSCognitoAuthentication
from flask_cognito_auth import CognitoAuthManager, callback_handler, logout_handler, login_handler
from flask_jwt_extended import set_access_cookies, JWTManager, verify_jwt_in_request, get_jwt_identity, jwt_required, \
    create_access_token
from flask_table import Table, Col, DatetimeCol
from boto3.dynamodb.conditions import Key, Attr
import boto3
import datetime
from flask_bootstrap import Bootstrap
import logging
import jwt

from werkzeug.security import generate_password_hash, check_password_hash

application = Flask(__name__)

application.secret_key = "my super secret keydfhsredhsdthsdtfghwtdjhnsaerz"

application.config['COGNITO_REGION'] = "us-east-1"
application.config['COGNITO_USER_POOL_ID'] = "us-east-1_U2ee9cQbf"
application.config['COGNITO_CLIENT_ID'] = "5r106vf47rhblal0a1d2bjm9g0"
application.config['COGNITO_CLIENT_SECRET'] = "kb0dvo1baefkui1fioarusddvms8rgt5uis7pa8cmb774eeuvul"
application.config['COGNITO_DOMAIN'] = "https://irrigationplanner.auth.us-east-1.amazoncognito.com"
# application.config["ERROR_REDIRECT_URI"] = "page500"        # Optional
# application.config["COGNITO_STATE"] = "mysupersecrethash"   # Optional

application.config['COGNITO_REDIRECT_URI'] = "https://irrigationplanner.com/cognito/callback"  # Specify this url in Callback URLs section of Appllication client settings of User Pool within AWS Cognito Sevice. Post login application will redirect to this URL

application.config['COGNITO_SIGNOUT_URI'] = "https://irrigationplanner.com/" # Specify this url in Sign out URLs section of Appllication client settings of User Pool within AWS Cognito Sevice. Post logout application will redirect to this URL

cognito = CognitoAuthManager(application)
# cognito = CognitoManager(app)
# cognito.init(app)

application.config["JWT_SECRET_KEY"] = "sadlfhbkjadsbfkjasdblfabsnelifhawsli"  # Change this!
jwt = JWTManager(application)


bootstrap = Bootstrap(application)
dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")


#
# application.add_url_rule('/', 'index', (lambda: root()))
# application.add_url_rule('/farmView', 'farmView', (lambda: farmView()))

# Use @login_handler decorator on cognito login route
@application.route('/cognito/login', methods=['GET'])
@login_handler
def cognitologin():
    pass

# Use @callback_handler decorator on your cognito callback route
@application.route('/cognito/callback', methods=['GET'])
@callback_handler
def callback():
    print("Do the stuff before post successfull login to AWS Cognito Service")

    for key in list(session.keys()):
        print(f"Value for {key} is {session[key]}")
    response = redirect(url_for("farmView"))
    return response

# @application.route('/home', methods=['GET'])
# def home():
#     current_user = session["username"]
#     email = session["email"]
#     return jsonify(logged_in_as=current_user, email=email), 200

# Use @logout_handler decorator on your cognito logout route
@application.route('/cognito/logout', methods=['GET'])
@logout_handler
def cognitologout():
    pass


@application.route('/', methods=['GET', 'POST'])
def root():
    # error = None
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        return render_template('farmView.html')
    #     name = request.form.get("name")
    #     password = request.form.get("password")
    # if request.method == 'POST':
    #     if request.form['username'] != 'admin' or request.form['password'] != 'admin':
    #         error = 'Invalid Credentials. Please try again.'
    #     else:
    #         return redirect('farmView.html', farmId=1)
    # return render_template('index.html', error=error)

@application.route('/.well-known/acme-challenge/IsflFAyZVa5XpaRJi2GDdvCa2P18GAtuQ83EHlNlbRw')
def cert():
    response = make_response("IsflFAyZVa5XpaRJi2GDdvCa2P18GAtuQ83EHlNlbRw.cLbPFSWwWpdX2PnKW_0o_AI1NHOa_Tu2pT-py9s1x1A", 200)
    response.mimetype = "text/plain"
    return response


@application.route('/farmView', methods=['GET', 'POST'])
# @jwt_required()
def farmView():
    # todo adjust this to work with login information
    email = session["email"]
    #email = "megan@freedman.co.nz"
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    usersTable = dynamodb.Table("users")
    userInfo = usersTable.query(KeyConditionExpression=Key("Email address").eq(email))

    userInfo1 = userInfo["Items"]
    consentNo = userInfo1[0]["Consent number"]
    moistureLevelsTable = dynamodb.Table('moistureLevels')
    waterRestrictionTable = dynamodb.Table('WaterRestriction')
    tableItems = []
    restrictionItems = []

    card = ["test1", "test2"]

    for i in range(20):
        moistureData = moistureLevelsTable.query(
            KeyConditionExpression=Key('fieldNo').eq(i) & Key("consentNo").eq(consentNo))
        for data in moistureData["Items"]:
            fieldNo = data["fieldNo"]
            device_data = data["device_data"]
            fieldMoist = device_data["fieldMoist"]
            fieldMoist = fieldMoist["BOOL"]
            tableItems.append(Item(consentNo, fieldNo, fieldMoist))
    moistureLevelsTable = ItemTable(tableItems, classes=["table"])
    waterRestrictionsData = waterRestrictionTable.scan()
    for i in waterRestrictionsData["Items"]:
        restrictionItems.append(i)
    for key in restrictionItems:
        if consentNo == key["consentNo"]:
            restriction = str(int(key["restriction"])) + "%"
            return render_template("farmView.html", table=moistureLevelsTable, restriction=restriction, card=card,
                                   date="Dec 10")
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
