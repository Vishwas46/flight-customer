from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps 
from pprint import pprint as pp
import string, random
import datetime


# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgresqldbuser:Flight1!@flight-customer-postgresqldbserver/postgresqldatabase12597'

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

    def __init__(self,passNumber,name,flightNumber,ticketNumber,seat):
        self.passNumber=passNumber
        self.name=name
        self.flightNumber=flightNumber
        self.ticketNumber=ticketNumber
        self.seat=seat
        self.seatLabel=seatLabel
        self.seatRow=seatRow


    def __repr__(self):
        return '<seat %r>' % self.seat

# BasicAuth
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == 'username' and auth.password == 'password':
            return f(*args, **kwargs)

        return make_response('Could not verify your login!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    return decorated

# @app.route mapps url to a python function
# index method gets all data from the database and displays it on the terminal. It also adds a flight to the database. 
@app.route('/')
@auth_required
def index():
    for u in Flight.query.all():
        print(u.__dict__)
    return render_template('addFlight.html')

@app.route('/v1/flight/<flight_number>')
def get_flight(flight_number):
    flight = Flight.query.filter_by(flightNumber=flight_number).first()
    #return jsonify(flight)
    print(flight.__dict__)
    return 'flight details shown in the terminal' 


@app.route('/postFlight', methods=['POST'])
def postFlight():
    flight = Flight(request.form['flightNumber'], request.form['start'], request.form['end'], request.form['date'], request.form['aircraft'])
    db.session.add(flight)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/v1/flight/<flight_number>', methods=['DELETE'])
def del_flight(flight_number):
    flight = Flight.query.filter_by(flightNumber=flight_number).first()
    db.session.delete(flight)
    db.session.commit()
    return 'flight deleted' 

@app.route('/v1/ticket', methods=['POST'])
def bookFlight():
    content = request.get_json()
    ticketNum = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    customer = Customer(content['passNumber'], content['name'], content['flightNumber'], ticketNum , '', '', '')
    db.session.add(customer)
    db.session.commit()
    print('Location: /v1/ticket/' + ticketNum)
    return ticketNum

@app.route('/v1/ticket/<ticket_number>', methods=['GET'])
def getFlight(ticket_number):
    customer = Customer.query.filter_by(ticketNumber=ticket_number).first()
    #return jsonify(customer)
    print(customer.__dict__)
    return 'ticket details shown'

@app.route('/v1/ticket/<ticket_number>', methods=['DELETE'])
def del_ticket(ticket_number):
    ticket = Customer.query.filter_by(ticketNumber=ticket_number).first()
    db.session.delete(ticket)
    db.session.commit()
    return 'flight deleted'

@app.route('/v1/seat/', methods=['POST'])
def sel_seat():
    content = request.get_json()
    cust = Customer.query.filter_by(ticketNumber=content['ticket-number']).first()
    cust.seatLabel = content['Seat-label']
    cust.seatRow = content['Seat-row']
    cust.seat = content['Seat-label'] + content['Seat-row']
    db.session.commit()
    print('Location: /v1/seat/' + content['ticket-number'] + '-' + cust.seat )
    return cust.seat

@app.route('/v1/seat/<seat>', methods=['DELETE'])
def del_seat(seat):
    tickNum, seatNum = seat.split("-")
    delSeat = Customer.query.filter_by(ticketNumber=tickNum).first()
    delSeat.seat = ''
    delSeat.seatLabel = ''
    delSeat.seatRow = ''
    db.session.commit()
    return "seat deleted"

@app.route('/v1/checkin', methods=['POST'])
def checkin():
    label = "ABCDEFGH"
    row = range(1,10)
    x = [{str(y) + ltr:'Empty' for ltr in label} for y in row]
    pp(x[1]['1A'])
    content = request.get_json()
    cust = Customer.query.filter_by(ticketNumber=content['ticket-number']).first()
    '''if cust.seat == '':
        label = label + 1
        row = row + 1
        print(label)
        '''
    return 'checked in'

@app.route('/v1/ticket/<ticknum>/notifications', methods=['GET'])
def notify(ticknum):
    if(ticknum=='1'):
        print('title: Booking Successful')
        print("message: Your ticket booking", ticknum, "is successful")
        print('timestamp:', datetime.datetime.now())
    
    return 'notified'


if __name__ == '__main__':
	app.run(debug=True)

