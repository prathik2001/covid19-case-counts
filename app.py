import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, g
from flask_table import Table, Col, DateCol

app = Flask(__name__, template_folder='templates') 

@app.route('/', methods=['GET', 'POST'])
def home():
	
	class ItemTable(Table):
	    Town = Col('Town')
	    Confirmed_Cases_Cummulative = Col('Confirmed Cases (cummulative)')
	    Deaths = Col('Deaths')
	    Recovered = Col('Recovered')
	    Notes = Col('Notes')
	    Source = Col('Source')
	    Updated = Col('Last Updated')

	scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
	service_account_info = json.load(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
	creds = ServiceAccountCredentials.from_service_account_info(service_account_info)
	client = gspread.authorize(creds)

	sheet = client.open("Massachusetts Coronavirus Info by Town - Source").sheet1
	read_object = sheet.get_all_records()

	table = ItemTable(read_object, table_id='cases')

	return render_template('covid.html', table = table, header = sheet.get('J346:M346'))

if __name__ == '__main__':
    app.run(debug=True)
    