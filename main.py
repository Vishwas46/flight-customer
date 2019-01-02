from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps 
from pprint import pprint as pp
import string, random
import datetime


# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:test@localhost/TestFlask'

# Create database connection object
db = SQLAlchemy(app)


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
    for u in Flight.query.all():
        print(u.__dict__)
    return render_template('addFlight.html')

@app.route('/v1/flight', methods=['POST'])
@auth_required_flight
def postFlight():
    content = request.get_json()
    flightNum = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    flight = Flight(flightNum, content['start'], content['end'], content['departure'], content['aircraft'])
    db.session.add(flight)
    db.session.commit()
    print('Location: /v1/flight/'+flightNum)
    return 'Flight Posted'

@app.route('/v1/flights', methods=['GET'])
@auth_required_flight
def get_all_flights():
    flights = Flight.query.all()
    for flight in flights:
        print(flight.__dict__)
    return 'all flights are shown in the terminal' 

@app.route('/v1/flight/<flight_number>', methods=['GET'])
@auth_required_flight
def get_flight(flight_number):
    flight = Flight.query.filter_by(flightNumber=flight_number).first()
    print(flight.__dict__)
    return 'flight details are shown in the terminal' 


@app.route('/v1/flight/<flight_number>', methods=['DELETE'])
@auth_required_flight
def del_flight(flight_number):
    flight = Flight.query.filter_by(flightNumber=flight_number).first()
    db.session.delete(flight)
    db.session.commit()
    return 'flight deleted' 

@app.route('/v1/ticket', methods=['POST'])
#@auth_required_customer
def bookFlight():
    content = request.get_json()
    ticketNum = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    customer = Customer(content['pass-number'], content['name'], content['flight-number'], ticketNum , '', '', '',1)
    db.session.add(customer)
    db.session.commit()
    print('Location: /v1/ticket/' +ticketNum)
    return 'flight booked'

@app.route('/v1/ticket/<ticket_number>', methods=['GET'])
@auth_required_customer
def getFlight(ticket_number):
    customer = Customer.query.filter_by(ticketNumber=ticket_number).first()
    #return jsonify(customer)
    print(customer.__dict__)
    return 'ticket details shown'

@app.route('/v1/ticket/<ticket_number>', methods=['DELETE'])
@auth_required_customer
def del_ticket(ticket_number):
    ticket = Customer.query.filter_by(ticketNumber=ticket_number).first()
    db.session.delete(ticket)
    db.session.commit()
    return 'flight deleted'

@app.route('/v1/seat', methods=['POST'])
#@auth_required_customer
def sel_seat():
    content = request.get_json()
    cust = Customer.query.filter_by(ticketNumber=content['ticket-number']).first()
    cust.seatLabel = content['Seat-label ']
    cust.seatRow = content['Seat-row']
    cust.seat = content['Seat-label '] + content['Seat-row']
    cust.status = 2
    db.session.commit()
    print('Location: /v1/seat/' + content['ticket-number'] + '-' + cust.seat )
    return 'seat booked'

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
    cust = Customer.query.filter_by(ticketNumber=ticknum).first()
    if(cust.status == 1):
        print('title: Booking Successful')
        print("message: Your ticket booking", ticknum, "is successful")
        print('timestamp:', datetime.datetime.now())
    elif(cust.status == 2):
        print('title: Seat Booking')
        print('seat', cust.seat, 'is booked for your ticket', ticknum)
        print('timestamp:', datetime.datetime.now())
    else:
        print('none')

    
    return 'notified'


if __name__ == '__main__':
	app.run(debug=True)

