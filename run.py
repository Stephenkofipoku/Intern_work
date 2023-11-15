import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import subprocess
import sys
import os

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)

# Function to load data from Google Sheets
def load_data(sheet_name, worksheet_name):
    sheet = GSPREAD_CLIENT.open(sheet_name).worksheet(worksheet_name)
    data = sheet.get_all_values()
    headers = data[0]
    values = data[1:]
    df = pd.DataFrame(values, columns=headers)
    return df

# Load data from Google Sheets
appointments_df = load_data('p21_bi_intern_test_appointments', 'appointments')
revenues_df = load_data('p21_bi_intern_test_revenues', 'revenues')

# Merge datasets
merged_df = pd.merge(appointments_df, revenues_df, on='appointment_id', how='left')

# Handle missing or null values in the revenue column
merged_df['revenue'] = pd.to_numeric(merged_df['revenue'], errors='coerce')

# Identify launch dates for each clinic
launch_dates = {
    'clinic_1': pd.to_datetime('2022-01-01'),
    'clinic_2': pd.to_datetime('2022-01-01'),
    'clinic_3': pd.to_datetime('2023-03-01'),
    'clinic_4': pd.to_datetime('2023-07-01')
}

# Extrapolate data for each clinic
extrapolated_dfs = {}
for clinic_id, launch_date in launch_dates.items():
    if clinic_id in ['clinic_1', 'clinic_2']:
        # For clinics 1 and 2, extrapolate for the entire 2023
        extrapolation_period = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    else:
        # For clinics 3 and 4, extrapolate from launch date to the end of 2023
        extrapolation_period = pd.date_range(start=launch_date, end='2023-12-31', freq='D')

    # Create a template DataFrame for extrapolation
    template_data = {
        'appointment_id': [f'extrap_{i}' for i in range(1, len(extrapolation_period) + 1)],
        'practitioner_id': ['extrap_practitioner'] * len(extrapolation_period),
        'patient_id': ['extrap_patient'] * len(extrapolation_period),
        'clinic_id': [clinic_id] * len(extrapolation_period),
        'appointment_date': extrapolation_period,
        'revenue': [0.0] * len(extrapolation_period)
    }

    # Create the extrapolated DataFrame based on the template
    extrapolated_data = pd.DataFrame(template_data)
    extrapolated_dfs[clinic_id] = extrapolated_data

# Combine extrapolated data for all clinics
extrapolated_all = pd.concat(extrapolated_dfs.values(), ignore_index=True)

# Combine historical data and extrapolated data
data_all = pd.concat([merged_df, extrapolated_all], ignore_index=True)

# Calculate total revenue for each clinic
total_revenue_by_clinic = data_all.groupby('clinic_id')['revenue'].sum()

# Count unique patients for all clinics
unique_patients_all = data_all['patient_id'].nunique()

# Print to the console
print("\nEstimates for All Clinics in 2023:")
print("Total Revenue by Clinic:")
print(total_revenue_by_clinic.reset_index())  # Reset index to display clinic_id
print(f"\nTotal Revenue: {total_revenue_by_clinic.sum()}")
print(f"Unique Patients: {unique_patients_all}")

# Redirect standard output to a text file
output_file = 'output.txt'
with open(output_file, 'w') as f:
    # Use a context manager to capture the output
    with redirect_stdout(f):
        # Print to the file
        print("\nEstimates for All Clinics in 2023:")
        print("Total Revenue by Clinic:")
        print(total_revenue_by_clinic.reset_index())  # Reset index to display clinic_id
        print(f"\nTotal Revenue: {total_revenue_by_clinic.sum()}")
        print(f"Unique Patients: {unique_patients_all}")

