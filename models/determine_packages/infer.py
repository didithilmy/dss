import os
import json
import pandas as pd
from sklearn.linear_model import LinearRegression

input_path = os.getenv('X_INPUT_DATA_FILE')
output_path = os.getenv('X_OUTPUT_DATA_FILE')

def read_data():    
    with open(input_path, 'r') as f:
        return json.loads(f.read())

def generate_output():
    return [
        {
            'draft_package_id': 'P0001',
            'date': '2020-07-01',
            'region_code': '1101',
            'price': 18000,
            'quota': 5000
        },
        {
            'draft_package_id': 'P0002',
            'date': '2020-07-01',
            'region_code': '1101',
            'price': 18000,
            'quota': 5000
        }
    ]

def execute():
    input_data = json.loads(read_data())
    date = input_data['date']
    data_packages = input_data['data_packages']
    hist_pricing_data = input_data['hist_pricing_data']
    hist_market_info = input_data['hist_market_info']

    df_hist_pricing_data = pd.DataFrame(data=hist_pricing_data)
    df_hist_market_info = pd.DataFrame(data=hist_market_info)