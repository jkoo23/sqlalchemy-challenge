# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return (
        f"Welcome to my climate app!<br/>"
        f"List of Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
@app.route('/api/v1.0/precipitation')
def precipitation():
    date_prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= (dt.date(2017,8,23) - dt.timedelta(days=365))).all()
    date_prcp_df = pd.DataFrame(date_prcp, columns = ['date','prcp'])
    date_prcp_df = date_prcp_df.sort_values(by=['date'])
    date_prcp_dict = date_prcp_df.to_dict('records')
    session.close()
    return jsonify(date_prcp_dict)

@app.route('/api/v1.0/stations')
def stationpage():
    station_list = session.query(Station.station).all()
    stat_list = list(np.ravel(station_list))
    session.close()
    return jsonify(stat_list)

#Query the dates and temperature observations of the most-active station for the previous year of data.
#Return a JSON list of temperature observations for the previous year.
@app.route('/api/v1.0/tobs')
def mostactivetobs():
    most_active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    most_active_tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= (dt.date(2017,8,23) - dt.timedelta(days=365))).\
        filter(Measurement.station == most_active_stations[0][0]).all()
    most_active_t = list(np.ravel(most_active_tobs))
    session.close()
    return jsonify(most_active_t)

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route('/v1.0/<start>')
def starthere(start):
    start_time = dt.datetime.strptime(start, '%Y-%m-%d')
    sel = [func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)]
    spec_start = session.query(*sel).\
        filter(Measurement.date >= start_time).all()
    sp_start = list(np.ravel(spec_start))
    session.close()
    return jsonify(sp_start)
    
@app.route('/api/v1.0/<start>/<end>')
def startend(start,end):
    start_time = dt.datetime.strptime(start, '%Y-%m-%d')
    end_time = dt.datetime.strptime(end, '%Y-%m-%d')
    sel = [func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)]
    spec_span = session.query(*sel).\
        filter(Measurement.date >= start_time).\
        filter(Measurement.date <= end_time).all()
    sp_start_end = list(np.ravel(spec_span))
    session.close()
    return jsonify(sp_start_end)

if __name__ == "__main__":
    app.run(debug=True)