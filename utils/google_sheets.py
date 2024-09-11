import gspread
import pandas as pd
from datetime import datetime
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('ashborn-ff-48ba96983ef1.json', scope)
google_client = gspread.authorize(creds)

def get_ssbu_results():
    sheet = google_client.open("SSBU Results").sheet1
    df = get_as_dataframe(sheet)

    df = df[['Piers Character', 'Rory Character', 'Piers Stocks', 'Rory Stocks', 'Date Played']].copy()
    df['Winner'] = df['Piers Stocks'].apply(lambda x: 'Piers' if x > 0 else 'Rory')
    df = df[df['Piers Stocks'] >= 0]

    return df

def save_results(p_char, r_char, p_stock, r_stock):
    sheet = google_client.open("SSBU Results").sheet1
    df = get_as_dataframe(sheet)

    new_data = pd.DataFrame({
        'Piers Character': [p_char],
        'Rory Character': [r_char],
        'Piers Stocks': [p_stock],
        'Rory Stocks': [r_stock],
        'Winner': ['Piers' if p_stock > 0 else 'Rory'],
        'Date Played': [datetime.now()]
    })

    dfmerged = pd.concat([df, new_data], ignore_index=True, sort=False)
    sheet.clear()
    set_with_dataframe(sheet, dfmerged)

    return dfmerged