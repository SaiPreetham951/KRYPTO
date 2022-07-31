import hashlib
import datetime
import pymongo
from pymongo import MongoClient
from flask import Flask, request, jsonify, url_for,redirect
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'BCDAE6AC377A842DDC9239F377D8100D8C98B8F3C15479598E2CFA675E5E98A5'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)


client = pymongo.MongoClient("mongodb+srv://SAI:1234@alertapp.4dksv.mongodb.net/?retryWrites=true&w=majority")
db = client["kryptoalertapp"]
users_collection = db["users"]
creds_info = db["userwallets"]

tok = ""
username = ""
password = ""

@app.route('/user/signup/', methods=['POST'])
def signup():
    if request.method == 'POST':
        new_user = request.get_json()  # store the json body request
        new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()  # encrpt password
        doc = users_collection.find_one({"username": new_user["username"]})  # check if user exist
        if not doc:
            users_collection.insert_one(new_user)
            return jsonify({'msg': 'User created successfully'}), 201
        else:
            return jsonify({'msg': 'Username already exists'}), 409

@app.route('/user/sigin/', methods=['POST'])
def signin():
    if request.method == 'POST':
        login_details = request.get_json()
        user_from_db = users_collection.find_one({'username': login_details['username']})

        if user_from_db:
            username = login_details['username']
            encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
            if encrpted_password == user_from_db['password']:
                access_token = create_access_token(identity=user_from_db['username'])  # create jwt token
                tok = access_token
                return jsonify(access_token=access_token), 200
        return jsonify({'msg' : 'Incorrect Username or Password'})

@app.route('/credit', methods = ['POST'])
def credit():
    if request.method == 'POST':
        if not tok:
            return redirect('http://127.0.0.1:5000/user/sigin/', code=302)
        else:
            new_cred = request.get_json()
            doc = creds_info.find_one({"username": new_cred["username"]})
            if not doc:
                creds_info.insert_one(new_cred)
            #for update balance
            else:
                for data in doc['coins']:
                    coinname = data['cname']
                    if coinname == doc["coinname"]:
                        oldquant = int(data['quantity'])
                        newquant = oldquant + int(doc['quantity'])
                        data['quantity'] = newquant
                coins = {{"$set": doc["coins"]}}
                creds_info.update_one(doc,coins)
            return "credited"

@app.route('/debit', methods = ['POST'])
def debit():
    if request.method == 'POST':
        if not tok:
            return redirect('http://127.0.0.1:5000/user/sigin/', code=302)
        else:
            new_cred = request.get_json()
            doc = creds_info.find_one({"username": new_cred["username"]})
            if not doc:
                creds_info.insert_one(new_cred)
            #for update balance
            else:
                for data in doc['coins']:
                    coinname = data['cname']
                    if coinname == doc["coinname"]:
                        oldquant = int(data['quantity'])
                        newquant = oldquant - int(doc['quantity'])#old Balance - removing balance
                        data['quantity'] = newquant
                coins = {{"$set": doc["coins"]}} #update the DB
                creds_info.update_one(doc,coins)
            return "credited"

@app.route('/credit/view', methods=['GET'])
def viewcred():
    if not tok:
        return jsonify({'msg' : 'Not Authorized'})
        #return redirect('http://127.0.0.1:5000/user/sigin/', code=302)
    else:
        if request.method == "GET":
            x = creds_info.find()
            s = []
            for i in x:
                s.append(str(i))
            return jsonify(s)

if __name__ == '__main__':
    app.run(debug=True)
