import pangres
import requests
import os
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def massachusetts():
	# Gets url to download file.
	domain = "https://www.mass.gov"
	source = requests.get("https://www.mass.gov/info-details/covid-19-response-reporting")
	soup = BeautifulSoup(source.content, 'html.parser')
	element = soup.find(text=re.compile('Raw data used to create the Weekly Public Health Report'))
	element = element.find_next_sibling('a')
	download_url = domain + element['href']
	headers = {
			"Host": "www.mass.gov",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Language": "en-US,en;q=0.5",
			"Accept-Encoding": "gzip, deflate, br",
			"Connection": "keep-alive",
			"Referer": "https://www.mass.gov/info-details/covid-19-response-reporting"
	}

	# Retrieves filename.
	file = requests.get(download_url, allow_redirects=True)
	filename = file.headers.get('content-disposition')
	filename = re.findall('filename=(.+)', filename)
	filename = re.findall(r'"([^"]*)"', filename[0]) #regex to find text within double quotes
	# At this stage, filename[0] gives filename.

	# Saves file locally and loads into dataframe. READ_EXCEL REQUIRES XLRD DEPENDENCY.
	open(filename[0], 'wb').write(file.content)
	df = pd.read_excel(filename[0], sheet_name="City_town", usecols="A:D,H,I", na_values="*")
	df['Percent positivity'] = df['Percent positivity'].multiply(100)
	df = df.where(df!="<5",df["Positive Tests Last 14 days"],axis=0)
	df = df.drop(columns=["Positive Tests Last 14 days"])
	# Uploads dataframe to Postgres database.
	table_name = 'massachusetts'
	engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'))
	
	df.set_index('City/Town', inplace=True)
	df = pangres.fix_psycopg2_bad_cols(df)
	pangres.upsert(engine=engine, df=df, table_name=table_name, if_row_exists='update')


if __name__ == '__main__':
	massachusetts()