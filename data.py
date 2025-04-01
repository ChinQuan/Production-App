import pandas as pd
import os

def load_data():
    if os.path.exists('production_data.csv'):
        return pd.read_csv('production_data.csv')
    else:
        return pd.DataFrame(columns=[
            'Date', 'Company', 'Seal Count', 'Operator', 'Seal Type',
            'Production Time (Minutes)', 'Downtime (Minutes)', 'Reason for Downtime'
        ])

def save_data(df):
    df.to_csv('production_data.csv', index=False)

