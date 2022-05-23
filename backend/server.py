import json
from flask_cors import CORS
from sqlalchemy import and_
from flask import Flask, make_response, request
from functools import wraps

from amazon import Amazon
from db import *
from interface import *

import jwt

SECRET = '123k123421kja-sdf'
app = Flask(__name__)
CORS(app=app)

# session = sessionmaker(bind=engine)()
session = create_db_session()

@app.route('/signup', methods=['POST'])
def signUp():
    '''user sign up

    returns 200 on success, 409 on email already exists
    
    '''
    email = request.form.get('email')
    name = request.form.get('name')
    upsName = request.form.get('upsName')
    password = request.form.get('password')
    locationX = request.form.get('location_x')
    locationY = request.form.get('location_y')

    usersSameEmail = session.query(Users).filter((Users.email == email))
    if(usersSameEmail.count() > 0):
        return make_response(json.dumps({"message": "user already exists"}), 409)

    newUser = Users(
        email=email, 
        name=name, 
        ups_name=upsName,
        password=password,
        location_x=locationX,
        location_y=locationY
    )
    
    session.add(newUser)
    session.commit()

    return make_response(json.dumps({"message": "ok"}), 200)

@app.route('/login', methods=['POST'])
def login():
    '''user login
    
    returns 200 with token on success, 401 on fail

    '''
    email = request.form.get('email')
    password = request.form.get('password')
    user = session.query(Users).filter(and_(Users.email==email, Users.password==password))
    if(user.count() == 0):
        print('auth failed')
        return make_response(json.dumps({"message": "authentication failed"}), 401)

    token =jwt.encode({'email': email, 'name': user[0].name}, SECRET, algorithm="HS256")    
    return make_response(
        json.dumps({
            "message": "ok",
            "token": token
        }), 
        200
    )

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
           token = request.headers['x-access-tokens']

        if token == None:
            return make_response(json.dumps({"message": "token missing"}), 401)
        # try:
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        user = session.query(Users).filter(Users.email==data['email'])
        if(user.count() == 0):
            return make_response(json.dumps({"message": "invalid token"}), 401)
        print(user[0].email)
        return f(user[0], *args, **kwargs)
        # except:
        #     return make_response(json.dumps({"message": "server error"}), 500)
    return decorator

@app.route('/user', methods=['GET', 'POST'])
@token_required
def handle_updateUser(user: Users):
    '''update existing user info
    
    '''
    if(request.method == 'GET'):
        userInfo = {}
        userInfo['email'] = user.email
        userInfo['name'] = user.name
        userInfo['upsName'] = user.ups_name
        userInfo['password'] = user.password
        userInfo['location_x'] = user.location_x
        userInfo['location_y'] = user.location_y        

        return make_response(json.dumps({"message": "ok", "userInfo": userInfo}), 200)

    elif(request.method == 'POST'):
        print(request.form)
        user.name = request.form.get('name')
        user.ups_name = request.form.get('upsName')
        user.password = request.form.get('password')
        user.location_x = request.form.get('location_x')
        user.location_y = request.form.get('location_y')
        session.commit()
        token =jwt.encode({'email': user.email, 'name': user.name}, SECRET, algorithm="HS256")    

        return make_response(json.dumps({"message": "ok", "token": token}), 200)
    else:
        return make_response(json.dumps({"message": "method not allowed"}), 405)

@app.route('/stocks', methods=['GET'])
@token_required
def handle_stocks(user):
    amazon = Amazon()
    stocks = amazon.list_stocks(user)
    return make_response(json.dumps(stocks), 200)

@app.route('/cart', methods=['GET', 'POST'])
@token_required
def handle_cart(user):
    amazon = Amazon()
    if request.method == 'GET':
        stocks = amazon.list_cart(user)
        return make_response(json.dumps(stocks), 200)
    elif request.method == 'POST':
        amazon.update_cart(user, request.form.get('stockId'), request.form.get('amount'))
        return make_response(json.dumps({"message": "ok"}), 200)
    else:
        return make_response(json.dumps({"message": "method not allowed"}), 405)

@app.route('/deliveries', methods=['GET'])
@token_required
def handle_listDeliveries(user):
    amazon = Amazon()
    deliveries = amazon.list_deliveries(user)
    return make_response(json.dumps(deliveries), 200)

@app.route('/delivery', methods=['GET'])
@token_required
def handle_deliveryDetails(user):
    orderId = request.args.get('order_id')

    amazon = Amazon()
    delivery = amazon.get_delivery_details(orderId)
    return make_response(json.dumps(delivery), 200)

@app.route('/purchaseMore', methods=['POST'])
@token_required
def handle_purchaseMore(user):
    if(request.method == 'POST'):
        stockId = request.form.get('stockId')
        amount = 10

        amazon = Amazon()
        amazon.go_purchase_more(stockId, int(amount))

        return make_response(json.dumps({'message': 'ok'}), 200)
    else:
        return make_response(json.dumps({'message': 'method not allowed'}), 405)

@app.route('/purchaseMore/new', methods=['POST'])
@token_required
def handle_purchaseNew(user):
    if(request.method == 'POST'):
        description = request.form.get('description')
        count = request.form.get('count')

        amazon = Amazon()
        amazon.go_purchase_new(user, description, int(count))

        return make_response(json.dumps({'message': 'ok'}), 200)
    return make_response(json.dumps({'message': 'method not allowed'}), 405)

@app.route('/placeOrder', methods=['POST'])
@token_required
def handle_placeOrder(user: Users):
    orderId = request.form.get('orderId')

    amazon = Amazon()
    amazon.place_order(int(user.id), int(orderId))

    return make_response(json.dumps({'message': 'ok'}), 200)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
