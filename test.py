import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import datetime

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('cread_py.json', scope)
client = gspread.authorize(creds)

sheet = client.open('test_sp').sheet1

def insert(sheet):
    row = []
    dot = datetime.date.today()
    print(dot)
    row.append(str(dot))
    rent = input("Enter rent : ")
    row.append(str(rent))
    Last = input("Last unit : ")
    row.append(str(Last))
    print(row)
    sheet.insert_row(row, 2)

def last(sheet):
    row = sheet.row_values(2)
    print(row)

if __name__ == "__main__":
    #insert(sheet)
    last(sheet)
