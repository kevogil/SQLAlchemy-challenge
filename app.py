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
        "<i>/api/v1.0/[start_date format:yyyy-mm-dd]</i><br/>"
        "<i>/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]</i><br/>"
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
    precipitation_data = []
    for date,prcp  in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
               
        precipitation_data.append(prcp_dict)

    # Return JSON
    return jsonify(precipitation_data)




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
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["tobs"] = tobs
               
        tobs_data.append(prcp_dict)

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(tobs_data)



# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

# ## Hints

# * You will need to join the station and measurement tables for some of the queries.

# * Use Flask `jsonify` to convert your API data into a valid JSON response object.

if __name__ == "__main__":
    app.run(debug=True)