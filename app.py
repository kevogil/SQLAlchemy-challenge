import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station


# Flask setup
app = Flask(__name__)


@app.route("/")
def index():
    return (
        "<b><u>SQLAlchemy Challenge</b></u></h1><br/>"
        "<br/>"
        "Routes available:<br/>"
        "<i>/api/v1.0/precipitation</i><br/>"
        "<i>/api/v1.0/stations</i><br/>"
        "<i>/api/v1.0/tobs</i><br/>"
        "<i>/api/v1.0/[start_date] (yyyy-mm-dd)</i><br/>"
        "<i>/api/v1.0/[start_date]/[end_date] (yyyy-mm-dd)</i><br/>"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session to DB
    session = Session(engine)

    # Query all Precipitation
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= last_year).all()

    session.close()

    # Convert the list to Dictionary
    prcp_data = []
    for date,prcp  in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
               
        prcp_data.append(prcp_dict)

    # Return JSON
    return jsonify(prcp_data)



@app.route("/api/v1.0/stations")
def stations():
    # Create our session to DB
    session = Session(engine)

    # Query all stations
    results = session.query(station.station).all()

    session.close

    # Return a JSON list of stations from the dataset.
    stations_data = list(np.ravel(results))
    return jsonify(stations_data)



@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session to DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)    
    most_active_station = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()[0]
    results = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active_station).filter(measurement.date >= last_year).order_by(measurement.date).all()

    session.close

    # Convert the list to Dictionary
    tobs_data = []
    for date,tobs  in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
               
        tobs_data.append(tobs_dict)

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(tobs_data)



@app.route("/api/v1.0/<start_date>")
def start(start_date):
    # Create our session to DB
    session = Session(engine)

    # Calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date).all()

    session.close

    # Convert the list to Dictionary
    start_date_tobs_data = []
    for min,avg,max  in results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min_tobs"] = min
        start_date_tobs_dict["avg_tobs"] = avg
        start_date_tobs_dict["max_tobs"] = max
               
        start_date_tobs_data.append(start_date_tobs_dict)

    # Return a JSON list.
    return jsonify(start_date_tobs_data)



@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    # Create our session to DB
    session = Session(engine)

    # Calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    session.close

    # Convert the list to Dictionary
    start_end_date_tobs_data = []
    for min,avg,max  in results:
        start_end_date_tobs_dict = {}
        start_end_date_tobs_dict["min_tobs"] = min
        start_end_date_tobs_dict["avg_tobs"] = avg
        start_end_date_tobs_dict["max_tobs"] = max
               
        start_end_date_tobs_data.append(start_end_date_tobs_dict)

    # Return a JSON list.
    return jsonify(start_end_date_tobs_data)



if __name__ == "__main__":
    app.run(debug=True)