from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgresqldbuser:Flight1!@flight-customer-postgresqldbserver/postgresqldatabase12597'
db = SQLAlchemy(app)


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



# mapping urls to a python function
@app.route('/')
def index():
	return render_template('addFlight.html')

@app.route('/postFlight', methods=['POST'])
def postFlight():
    flight = Flight(request.form['flightNumber'], request.form['start'], request.form['end'], request.form['date'], request.form['aircraft'])
    db.session.add(flight)
    db.session.commit()
    return redirect(url_for('index'))

# delete after try
@app.route('/postjson', methods=['POST'])
def post():
    print(request.is_json)
    content = request.get_json()
    #print(content)
    print('ID = ' + content['id'])
    print('name = ' + content['name'])
    return 'JSON posted'

@app.route('/products')
def products():
    products = Flight.query.all()
    for prod in products:
        return prod.aircraft

if __name__ == '__main__':
	app.run(debug=True)
