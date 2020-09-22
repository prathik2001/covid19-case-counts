import os
import requests
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, render_template, request
from sqlalchemy import create_engine, Table

load_dotenv()
app = Flask(__name__, template_folder='templates') 
engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'))

@app.route('/', methods=['GET'])
def home():
	header_json = requests.get("https://api.covidtracking.com/v1/states/ma/current.json").json()

	header = []
	header.append(header_json['positive'])
	header.append(header_json['hospitalizedCurrently'])
	header.append(header_json['death'])
	header.append(header_json['lastUpdateEt'])

	table_df = pd.read_sql_table("massachusetts", con=engine)
	table = table_df.to_html(table_id="table", index=False)

	# Use different API to get header data.
	return render_template('home_massachusetts.html', table = table, header = header)

@app.route('/florida', methods=['GET'])
def florida():
	header_json = requests.get("https://api.covidtracking.com/v1/states/fl/current.json").json()
	
	header = []
	header.append(header_json['positive'])
	header.append(header_json['hospitalizedCurrently'])
	header.append(header_json['death'])
	header.append(header_json['lastUpdateEt'])

	table_df = pd.read_sql_table("florida", con=engine)
	rename_dict = {"COUNTYNAME": "County", "POName": "PO Name", "Places": "Cities", 
				   "Cases_1": "Cases"}
	columns = ["ZIP", "County", "PO Name", "Cities", "Cases"]
	table_df = table_df.rename(columns=rename_dict)
	table = table_df.to_html(table_id="table", columns=columns, index=False)

	# Use different API to get header data.
	return render_template('florida.html', table = table, header = header)

@app.route('/arizona', methods=['GET'])
def arizona():
	header_json = requests.get("https://api.covidtracking.com/v1/states/az/current.json").json()
	
	header = []
	header.append(header_json['positive'])
	header.append(header_json['hospitalizedCurrently'])
	header.append(header_json['death'])
	header.append(header_json['lastUpdateEt'])

	table_df = pd.read_sql_table("arizona", con=engine)
	rename_dict = {"POSTCODE": "ZIP", "ConfirmedCaseCount": "Confirmed Cases", "City Name": "Location"}
	table_df = table_df.rename(columns=rename_dict)
	table = table_df.to_html(table_id="table", index=False)

	# Use different API to get header data.
	return render_template('arizona.html', table = table, header = header)

if __name__ == '__main__':
	app.run()
    