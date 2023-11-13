import gspread
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd 

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

# Convert data to pandas DataFrames
appointments_df = pd.DataFrame(appointments_data[1:], columns=appointments_data[0])
revenues_df = pd.DataFrame(revenues_data[1:], columns=revenues_data[0])

# Convert 'revenue' column to numeric
revenues_df['revenue'] = pd.to_numeric(revenues_df['revenue'])

# Merge appointments and revenues on 'appointment_id'
merged_df = pd.merge(appointments_df, revenues_df, on='appointment_id', how='left')
