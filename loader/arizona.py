import json
import pangres
import requests
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def arizona():
	file = requests.get("https://adhsgis.maps.arcgis.com/sharing/rest/content/items/8a2c089c866940bbac0ee70a41ea27bd/data", allow_redirects=True)

	# Saves file locally and loads into dataframe. READ_EXCEL REQUIRES XLRD DEPENDENCY.
	open("COVID19CONFIRMED_BYZIP_excel.xls", 'wb').write(file.content)
	df = pd.read_excel("COVID19CONFIRMED_BYZIP_excel.xls", usecols="A,C")

	df.drop(df[df['ConfirmedCaseCount'] == "Data Suppressed"].index, inplace=True)
	# The code below is used to populate the database on first run with city names for each ZIP code.
	# citynames = [get_city_names(row) for row in df['POSTCODE']]
	# df.insert(loc=1, column="City Name", value=citynames)

	# Uploads dataframe to Postgres database.
	table_name = 'arizona'
	engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'))
	
	df.set_index('POSTCODE', inplace=True)
	df = pangres.fix_psycopg2_bad_cols(df)
	pangres.upsert(engine=engine, df=df, table_name=table_name, if_row_exists='update')

def get_city_names(row):
	r = requests.get("https://nominatim.openstreetmap.org/?addressdetails=1&q=" + row + ",AZ&format=json&limit=1")
	data = r.json()

	if len(data) == 0:
		return "Arizona"
	if data[0]['class'] != "place":
		return "Arizona"
	if "suburb" in data[0]['address']:
		location = data[0]['address']['suburb']
		if "city" in data[0]['address']:
			location = location + ', ' + data[0]['address']['city']
		if "county" in data[0]['address']:
			location = location + ', ' + data[0]['address']['county']
	elif "city" in data[0]['address']:
		location = data[0]['address']['city']
		if "county" in data[0]['address']:
			location = location + ', ' + data[0]['address']['county']
	elif "county" in data[0]['address']:
		location = data[0]['address']['county']
	else:
		location = "Arizona"
	return location;

if __name__ == '__main__':
	arizona()