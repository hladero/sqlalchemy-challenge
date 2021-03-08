## Step 2 - Climate App
#Import Dependencies
from flask import Flask
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect, create_engine



###############################################################################
#Database Setup
###############################################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect  database into a ORM
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
# Map classes Measurement
measurement=Base.classes.measurement
# Map classes Station
station=Base.classes.station
# Create our session (link) from Python to the DB
session = Session (bind=engine)


###############################################################################
#Flask Setup
###############################################################################
app = Flask(__name__)


###############################################################################
#Flask Routes
###############################################################################
@app.route("/")
def home_page():
    """List all routes that are available"""
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end <br/>"
        f"When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date <br/> "
        "When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive <br/>"
    )
    

#Define what to do when a user hits /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    prevYear = dt.datetime.strptime(most_recent_date,'%Y-%m-%d') - dt.timedelta(366)
    result = session.query(measurement.date, measurement.prcp).filter(measurement.date > prevYear).all()
    
    rain_data = []
    for x in result:
        data = {}
        data["date"] = result[0]
        data["prcp"] = result[1]
        rain_data.append(data)
    return jsonify(rain_data)

###############################################################################
#Define what to do when a user hits /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    list_stations = session.query(station.station, station.name).all()
    return jsonify(list_stations)


###############################################################################
#Define what to do when a user hits /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    prevYear = dt.datetime.strptime(most_recent_date,'%Y-%m-%d') - dt.timedelta(366)
    result1 = session.query(measurement.date, measurement.prcp).filter(measurement.date > prevYear).all()
    most_active_stations = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    result2=session.query(measurement.date, measurement.tobs).filter(measurement.date>prevYear).all()
    
#Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(result2)

###############################################################################
#Define what to do when a user hits /api/v1.0/start route
@app.route("/api/v1.0/start")
def startdate():
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    prevYear = dt.datetime.strptime(most_recent_date,'%Y-%m-%d') - dt.timedelta(366)
    Temp=session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs))\
.filter(measurement.date >= prevYear).all()
    return jsonify(Temp)

###############################################################################
#Define what to do when a user hits /api/v1.0/<start>/<end> route
@app.route("/api/v1.0/start/end")
def start_end_date():
    end_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    start_date = dt.datetime.strptime(end_date,'%Y-%m-%d') - dt.timedelta(366)
    Temp1=session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs))\
.filter(measurement.date.between(start_date ,end_date)).all()
    return jsonify(Temp1)


if __name__ == "__main__":
    app.run(debug=True)

