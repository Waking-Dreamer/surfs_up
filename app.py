# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd

# Import SQLAlchemy dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import Flask dependencies
from flask import Flask, jsonify

# Set up the database engine for the Flask application
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the database into classes
Base = automap_base()

# Reflect the database
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session link from Python to the database
session = Session(engine)

# Define Flask app
app = Flask(__name__)

# Define the welcome route (root route)
@app.route("/")

# Create a function to set up remaining routes
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

# Create precipitation route
@app.route("/api/v1.0/precipitation")

# Create precititation function
def precipitation():
    # calculates the date one year ago from the most recent date in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # get the date and precipitation for the previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
       filter(Measurement.date >= prev_year).all()
    # create a dictionary with the date as the key and the precipitation as the value
    precip = {date: prcp for date, prcp in precipitation}
    # retunr data as a JSON file
    return jsonify(precip)

# Create station route
@app.route("/api/v1.0/stations")

# Create station function
def stations():
    # Get all stations from the database
    results = session.query(Station.station).all()
    # Unravel the results into a one-dimensional array and convert into a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

# Create temperature route
@app.route("/api/v1.0/tobs")

# Create temperature function
def temp_monthly():
    # calculate the date one year ago from the last date in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # query the primary station for all the temperature observations from the previous year
    results = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= prev_year).all()
    # Unravel the results into a one-dimensional array and convert that array into a list. 
    temps = list(np.ravel(results))
    # Jsonify the list and return our results
    return jsonify(temps=temps)

# Create starting and ending date for the statistics route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

# Create statistics function
def stats(start=None, end=None):
    # Create a query to select the minimum, average, and maximum temperatures from the SQLite database
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    # Determine the starting and ending date. The asterisk is used to indicate there will be multiple results in the query: minimum, average, and maximum temperatures
    if not end:
        results = session.query(*sel).filter(Measurement.date <= start).all()
        # Unravel the results into a one-dimensional array, convert them to a list, jsonify the results, and return them.
        temps = list(np.ravel(results))
        return jsonify(temps)
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)