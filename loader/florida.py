import json
import pangres
import requests
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def florida():
	# Gets url to download file.
	source = requests.get("https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/Florida_Cases_Zips_COVID19/FeatureServer/0/query?where=0%3D0&outFields=*&outFields=ZIP,COUNTYNAME,POName,Cases_1&returnGeometry=false&f=json")

	# Retrieves filename.
	data = json.loads(source.text)

	rows = []
	for element in data["features"]:
		rows.append(element["attributes"])

	df = pd.DataFrame(rows)
	cols = [0,1,4,6,7,11]
	df = df[df.columns[cols]]

	# Uploads dataframe to Postgres database.
	table_name = 'florida'
	engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'))

	df.sort_values(by=['ZIP'], inplace=True)

	# Some ZIPs span multiple counties, but data is reported separately
	# for each county, so ZIP cannot be used as index column.
	df.set_index("OBJECTID", inplace=True)

	df = pangres.fix_psycopg2_bad_cols(df)
	pangres.upsert(engine=engine, df=df, table_name=table_name, if_row_exists='update')

if __name__ == '__main__':
	florida()