from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from functools import wraps 
from pprint import pprint as pp
import string, random
from datetime import datetime


# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:test@localhost/TestFlask'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgresqldbuser@flight-customer-postgresqldbserver:Flight1!@flight-customer-postgresqldbserver.postgres.database.azure.com/postgresqldatabase12597'

# Create database connection object
db = SQLAlchemy(app)
ma = Marshmallow(app)



# flight database with columns and its type
class Flight(db.Model):
    flightNumber = db.Column(db.String, primary_key=True)
    start = db.Column(db.String, nullable=False)
    end = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    aircraft = db.Column(db.String, nullable=False)

    def __init__(self,flightNumber,start,end,date,aircraft):
        self.flightNumber=flightNumber
        self.start=start
        self.end=end
        self.date=date
        self.aircraft=aircraft

    def __repr__(self):
        return '<date %r>' % self.date

# Customer database with columns and its type
class Customer(db.Model):
    passNumber = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    flightNumber = db.Column(db.String, nullable=False)
    ticketNumber = db.Column(db.String, nullable=True)
    seat = db.Column(db.String, nullable=True)
    seatLabel = db.Column(db.String, nullable=True)
    seatRow = db.Column(db.String, nullable=True)
    status = db.Column(db.Integer, nullable=True)

    def __init__(self,passNumber,name,flightNumber,ticketNumber,seat,seatLabel,seatRow,status):
        self.passNumber=passNumber
        self.name=name
        self.flightNumber=flightNumber
        self.ticketNumber=ticketNumber
        self.seat=seat
        self.seatLabel=seatLabel
        self.seatRow=seatRow
        self.status=status


    def __repr__(self):
        return '<seat %r>' % self.seat

class FlightSchema(ma.ModelSchema):
    class Meta:
        model = Flight

class CustomerSchema(ma.ModelSchema):
    class Meta:
        model = Customer

# BasicAuth
def auth_required_flight(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == 'flight' and auth.password == 'reachforyourstar':
            return f(*args, **kwargs)

        return make_response('Could not verify your login!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    return decorated

def auth_required_customer(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == 'customer' and auth.password == 'reached':
            return f(*args, **kwargs)

        return make_response('Could not verify your login!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    return decorated

# @app.route mapps url to a python function
# index method gets all data from the database and displays it on the terminal. It also adds a flight to the database. 
@app.route('/')
@auth_required_flight
def index():
    return 'home page'

@app.route('/v1/flight', methods=['POST'])
@auth_required_flight
def postFlight():
    content = request.get_json()
    flightNum = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    flight = Flight(flightNum, content['start'], content['end'], content['departure'], content['aircraft'])
    db.session.add(flight)
    db.session.commit()
    return 'Location: /v1/flight/'+flightNum

@app.route('/v1/flights', methods=['GET'])
@auth_required_flight
def get_all_flights():
    results = Flight.query.all()
    flight_schema = FlightSchema(many=True)
    output = flight_schema.dump(results).data
    return jsonify({'': output})

@app.route('/v1/flight/<flight_number>', methods=['GET'])
@auth_required_flight
def get_flight(flight_number):
    result = Flight.query.filter_by(flightNumber=flight_number).first()
    flight_schema = FlightSchema()
    output = flight_schema.dump(result).data
    return jsonify({'': output})


@app.route('/v1/flight/<flight_number>', methods=['DELETE'])
@auth_required_flight
def del_flight(flight_number):
    flight = Flight.query.filter_by(flightNumber=flight_number).first()
    db.session.delete(flight)
    db.session.commit()
    return 'flight deleted' 

@app.route('/v1/ticket', methods=['POST'])
@auth_required_customer
def bookFlight():
    content = request.get_json()
    ticketNum = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    customer = Customer(content['pass-number'], content['name'], content['flight-number'], ticketNum , '', '', '',1)
    db.session.add(customer)
    db.session.commit()
    return 'Location: /v1/ticket/' + ticketNum

@app.route('/v1/ticket/<ticket_number>', methods=['GET'])
@auth_required_customer
def getFlight(ticket_number):
    customer = Customer.query.filter_by(ticketNumber=ticket_number).first_or_404()
    customer_schema = CustomerSchema()
    output = customer_schema.dump(customer).data
    return jsonify({'': output})

@app.route('/v1/ticket/<ticket_number>', methods=['DELETE'])
@auth_required_customer
def del_ticket(ticket_number):
    ticket = Customer.query.filter_by(ticketNumber=ticket_number).first()
    db.session.delete(ticket)
    db.session.commit()
    return 'flight deleted'

@app.route('/v1/seat', methods=['POST'])
@auth_required_customer
def sel_seat():
    content = request.get_json()
    cust = Customer.query.filter_by(ticketNumber=content['ticket-number']).first()
    cust.seatLabel = content['Seat-label ']
    cust.seatRow = content['Seat-row']
    cust.seat = content['Seat-label '] + content['Seat-row']
    cust.status = 2
    db.session.commit()
    return 'Location: /v1/seat/' + content['ticket-number'] + '-' + cust.seat

@app.route('/v1/seat/<seat>', methods=['DELETE'])
@auth_required_customer
def del_seat(seat):
    tickNum, seatNum = seat.split("-")
    delSeat = Customer.query.filter_by(ticketNumber=tickNum).first()
    delSeat.seat = ''
    delSeat.seatLabel = ''
    delSeat.seatRow = ''
    delSeat.status = 1
    db.session.commit()
    return "seat deleted"

@app.route('/v1/checkin', methods=['POST'])
@auth_required_customer
def checkin():
    label = "ABCDEFGH"
    row = range(1,10)
    x = [{str(y) + ltr:'Empty' for ltr in label} for y in row]
    x[1]['1A'] = 'Test'
    pp(x)
    content = request.get_json()
    cust = Customer.query.filter_by(ticketNumber=content['ticket-number']).first()
    '''if cust.seat == '':
        label = label + 1
        row = row + 1
        print(label)
        '''
    return 'checked in'

@app.route('/v1/ticket/<ticknum>/notifications', methods=['GET'])
@auth_required_customer
def notify(ticknum):
    cust = Customer.query.filter_by(ticketNumber=ticknum).first_or_404()
    if(cust.status == 1):
        dt = datetime.now()
        return 'title: Booking Successful\n' + 'message: Your ticket booking ' + ticknum + ' is successful.\n' + 'timestamp: ' + str(dt)
        
    elif(cust.status == 2):
        dt = datetime.now()
        return 'title: Seat Booking\n' + 'seat ' + cust.seat + ' is booked for your ticket ' + ticknum + '\n' + 'timestamp: ' + str(dt)
    else:
        return 'none'

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return 'please check the input'

@app.errorhandler(403)
def forbidden(e):
    return 'you do not have the permissions'

@app.errorhandler(405)
def forbidden(e):
    return 'Please check the method name'

@app.errorhandler(500)
def serverError(e):
    return 'internal server error'

if __name__ == '__main__':
	app.run()

