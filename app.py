import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc, inspect

from flask import Flask, jsonify


#Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect an existing database into a new model
Base = automap_base()

#reflect the tables
Base.prepare(engine, reflect=True)

#Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup
app = Flask(__name__)

#Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #connect to database
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    precip_value = {date:prcp for date, prcp in results}


    return jsonify(precip_value)

@app.route("/api/v1.0/stations")
def stats():
    session = Session(engine)

    results = session.query(Station.station).all()

    session.close()

    stats_list = list(np.ravel(results))

    return jsonify(stats_list)
    
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    latest_date_dt = dt.date(2017, 8, 23)
    
    year_ago = latest_date_dt - dt.timedelta(days=365)
    
    active = session.query(Measurement.station, func.count(Measurement.station)).\
                  group_by(Measurement.station).\
                  order_by(func.count(Measurement.station).desc()).all()

    top = active[0][0]

    tobs = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
                  filter(Measurement.date >= year_ago).\
                  filter(Measurement.station == top).all()
    
    session.close()

    return jsonify(tobs)

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)

    weather = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    return jsonify(weather)

@app.route('/api/v1.0/<start>/<end>')
def startend(start, end):
    session = Session(engine)

    weather2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    return jsonify(weather2)

if __name__ == '__main__':
    app.run(debug=True)