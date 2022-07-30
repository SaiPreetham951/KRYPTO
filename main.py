import json
import pymongo
import requests
from flask import Flask, jsonify, request
from apscheduler.schedulers.blocking import BlockingScheduler
import pika


# creating app
app = Flask(__name__)
client = pymongo.MongoClient("mongodb+srv://SAI:1234@alertapp.4dksv.mongodb.net/?retryWrites=true&w=majority")
db = client["kryptoalertapp"]
users_collectio = db["alert"]

@app.route('/', methods=['GET'])
def home():
    if (request.method == 'GET'):
        data = "PRICE ALERT APP"
        return jsonify({'data': data})


@app.route('/alerts/create=<string:pair>', methods=['POST'])
def create(pair):
    content_type = request.headers.get('Content-Type')
    key = "https://api.binance.com/api/v3/ticker/price?symbol=" + pair
    data = requests.get(key)
    data = data.json()
    data = (data['price'])
    rdata = request.get_json()
    price = (rdata['price'])
    #return rdata
    users_collectio.insert_one(rdata)
    return jsonify({'CurrentPrice': data, 'AlertPrice: ': price}),initialize()

@app.route('/alerts/delete', methods=['GET', 'POST'])
def delete():
    content_type = request.headers.get('Content-Type')
    if (request.method == 'POST'):
        myquery = request.get_json()
        users_collectio.delete_one(myquery)
        return jsonify({'data': 'Alert Deleted'})


@app.route('/alerts/history', methods=['GET'])
def history():
    if (request.method == 'GET'):
        x = users_collectio.find()
        return jsonify({'data': x})

def initialize():
    x = users_collectio.find()
    s = []
    for i in x:
        s.append(str(i))
    y = json.dumps(s)
    z = json.loads(y)

    for datar in z:
        price = datar['price']
        key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        data = requests.get(key)
        data = data.json()
        data = data['price']
        tprice = int(price)
        tdat = int(datar)
        #initialize(tprice, tdat)
        scheduler = BlockingScheduler()
        scheduler.add_job(inpr(tdat,tprice), seconds=5)

def inpr(price,alert):
    with app.app_context():
        if(price  >= alert):
            sendmessage(price)


def sendmessage(price):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='', routing_key='hello', body=f'Price Crossed{price}')
    print(f'Price Crossed{price}')
    connection.close()

# driver func
if __name__ == '__main__':
    app.run(debug=True)