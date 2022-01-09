import gspread
from oauth2client.service_account import ServiceAccountCredentials

class Connection:

    def __init__(self, sheet, room):
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('/home/pi/scripts/rent_bot/cread_py.json', scope)
        client = gspread.authorize(creds)
        self.sheet = client.open(f"{sheet}").worksheet(f"{room}")

    def get_headings(self):
        h_items = self.sheet.row_values(1)
        return h_items

    def get_last_row(self):
        l_row = self.sheet.get_all_values()
        return l_row[-1], len(l_row)

    def add_data(self, row, data):
        add = self.sheet.insert_row(data, row)
