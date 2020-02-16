import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('cread_py.json', scope)
client = gspread.authorize(creds)

sheet = client.open('test_sp').sheet1

data = sheet.get_all_records()
#print(data)

pp = pprint.PrettyPrinter()
#pp.pprint(data)

# Reading values
column = sheet.col_values(6)
row = sheet.row_values(16)
perticular = sheet.cell(1, 1).value


#inserting values in spreadsheet
row = ["I'm","inserting","a","new","row","into","a,","Spreadsheet","using","Python"]
index = 2
sheet.insert_row(row, index)

#Update a particular cell
#sheet.update_cell(16, 11, "telemedicine_id")

#sheet.insert_columns(row, index)

cell_list = sheet.range('A3:E3')
#print(cell_list)
print(column)
