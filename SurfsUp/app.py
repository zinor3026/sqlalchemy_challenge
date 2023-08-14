# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify

from datetime import datetime

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with= engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    recent = dt.date(2017,8,23)
    one_year = recent - dt.timedelta(days = 365)
    data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year)
    
    session.close()
    pres = {date: prcp for date, prcp in data}
    
    return jsonify(pres)

@app.route("/api/v1.0/stations")
def stations():
    
    station_names = session.query(station.station).all()
    
    session.close()
    
    stations = list(np.ravel(station_names))
    
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temperature():
    
    recent = dt.date(2017,8,23)
    one_year = recent - dt.timedelta(days = 365)
    
    temp_data = session.query(measurement.tobs).filter(measurement.date >= one_year).filter(measurement.station == 'USC00519281').all()
    
    session.close()
    
    temp = list(np.ravel(temp_data))
    
    return jsonify(temp)

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def calc_temps(start, end=None):
     
    # Convert start and end dates to datetime objects
    start_date = datetime.strptime(start, '%Y-%m-%d')
    if end:
        end_date = datetime.strptime(end, '%Y-%m-%d')
    
    # Query to calculate TMIN, TAVG, and TMAX
    if end:
        results = session.query(func.min(measurement.tobs), 
                                func.avg(measurement.tobs), 
                                func.max(measurement.tobs)) \
                         .filter(measurement.date >= start_date, 
                                 measurement.date <= end_date) \
                         .all()
    else:
        results = session.query(func.min(measurement.tobs), 
                                func.avg(measurement.tobs), 
                                func.max(measurement.tobs)) \
                         .filter(measurement.date >= start_date) \
                         .all()
    
    session.close()
    
    # Convert the query result to a dictionary
    temp_data = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    
    return jsonify(temp_data)


if __name__ == '__main__':
    app.run(debug=True)

        