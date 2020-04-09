import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from flask_table import Table, Col
from csv import DictReader

class ItemTable(Table):
    Town = Col('Town')
    Confirmed_Cases_Cummulative = Col('Confirmed Cases (cummulative)')
    Deaths = Col('Deaths')
    Recovered = Col('Recovered')
    Notes = Col('Notes')
    Source = Col('Source')
    Updated = Col('Last Updated')

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

sheet = client.open("Massachusetts Coronavirus Info by Town").sheet1
read_object = sheet.get_all_records()

table = ItemTable(read_object)

print(table.__html__())