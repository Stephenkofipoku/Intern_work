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

# Convert 'appointment_date' to datetime
merged_df['appointment_date'] = pd.to_datetime(merged_df['appointment_date'])

# Create a new column 'clinic_launch' to identify when each clinic was launched
merged_df['clinic_launch'] = pd.to_datetime('2023-03-01')  # Assuming March 2023 launch for the first clinic
merged_df.loc[merged_df['clinic_id'].isin(['clinic_2', 'clinic_3']), 'clinic_launch'] = pd.to_datetime('2023-07-01')  # July 2023 launch for clinic_2 and clinic_3

# Filter data for 2023
data_2023 = merged_df[merged_df['appointment_date'].dt.year == 2023]

# Calculate total revenue for each clinic
total_revenue = data_2023.groupby('clinic_id')['revenue'].sum()

# Count unique patients for each clinic
unique_patients = data_2023.groupby('clinic_id')['patient_id'].nunique()

# Sum up total revenue and unique patient counts for all clinics
total_revenue_all = total_revenue.sum()
total_unique_patients_all = unique_patients.sum()