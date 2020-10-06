import os
import requests
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, Table
from sqlalchemy.orm import sessionmaker, scoped_session

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

	return render_template('arizona.html', table = table, header = header)

@app.route('/api/cases', methods=['GET'])
def get_json():
	Session = scoped_session(sessionmaker(bind=engine))
	s = Session()
	params = request.args
	num_params = len(request.args)

	state = params.get('state')
	city = params.get('city')
	zip_code = params.get('zip')
	county = params.get('county')

	query = "SELECT * FROM " + state

	if 'massachusetts' in state:
		if city:
			list_params = city.split(',')
			query_list = str(tuple([arg for arg in list_params])).replace(',)', ')')
			query += ' WHERE "City/Town" IN {query_list};'.format(query_list=query_list)
		res = s.execute(query)
		list_cases = [row for row in res]
		dictionary = {}
		i = 0
		for row in list_cases:
			dictionary[i] = {'town':list_cases[i][0],
				'cases':list_cases[i][1],
				'last2weekcases':list_cases[i][2],
				'casesper1k':list_cases[i][3],
				'percentpositive':list_cases[i][4],
			}
			i += 1	

	elif 'florida' in state:
		if city:
			list_params = city.split(',')
			query_list = str(tuple([arg for arg in list_params])).replace(',)', ')')
			query += ' WHERE "POName" IN {query_list};'.format(query_list=query_list)

		elif zip_code:
			list_params = zip_code.split(',')
			query_list = str(tuple([arg for arg in list_params])).replace(',)', ')')
			query += ' WHERE "ZIP"::integer IN {query_list};'.format(query_list=query_list)
		
		elif county:
			list_params = county.split(',')
			query_list = str(tuple([arg for arg in list_params])).replace(',)', ')')
			query += ' WHERE "COUNTYNAME" IN {query_list};'.format(query_list=query_list)

		res = s.execute(query)
		list_cases = [row for row in res]
		dictionary = {}
		i = 0
		for row in list_cases:
			dictionary[i] = {'id':list_cases[i][0],
				'zip':list_cases[i][1],
				'county':list_cases[i][2],
				'po_city':list_cases[i][3],
				'places':list_cases[i][4],
				'cases':list_cases[i][5]
			}
			i += 1	

	elif 'arizona' in state:
		if city:
			list_params = city.split(',')
			query_list = str(tuple(['%' + arg + '%' for arg in list_params])).replace(',)', ')')
			print(query_list)
			query += ' WHERE "City Name" LIKE {query_list};'.format(query_list=query_list)

		elif zip_code:
			list_params = zip_code.split(',')
			query_list = str(tuple([arg for arg in list_params])).replace(',)', ')')
			query += ' WHERE "POSTCODE"::integer IN {query_list};'.format(query_list=query_list)

		elif county:
			list_params = county.split(',')
			query_list = str(tuple(['%' + arg + '%' for arg in list_params])).replace(',)', ')')
			query += ' WHERE "City Name" LIKE {query_list};'.format(query_list=query_list)

		print(query)
		res = s.execute(query)
		list_cases = [row for row in res]
		dictionary = {}
		i = 0
		for row in list_cases:
			dictionary[i] = {'zip':list_cases[i][0],
				'cases':list_cases[i][1],
				'location':list_cases[i][2],
			}
			i += 1	

	s.close()
	return jsonify(dictionary)

if __name__ == '__main__':
	app.run(debug=True)
    