import gspread
import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
appointments_spreadsheet = GSPREAD_CLIENT.open('p21_bi_intern_test_appointments')
revenues_spreadsheet = GSPREAD_CLIENT.open('p21_bi_intern_test_revenues')

# Access worksheets
appointments_worksheet = appointments_spreadsheet.worksheet('appointments')
revenues_worksheet = revenues_spreadsheet.worksheet('revenues')

# Get data from worksheet
appointments_data = appointments_worksheet.get_all_values()
revenues_data = revenues_worksheet.get_all_values()

print("Appointments Data:")
print(appointments_data)

print("Revenues Data:")
print(revenues_data)