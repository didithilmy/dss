import os
import json
from random import randrange
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

input_path = os.getenv('X_INPUT_DATA_FILE')
output_path = os.getenv('X_OUTPUT_DATA_FILE')

linreg = LinearRegression()


def read_data():
    with open(input_path, 'r') as f:
        return json.loads(f.read())


def train(df):
    x = df['year'].to_numpy().reshape(-1, 1)
    y = df['price_per_gb'].to_numpy()

    linreg.fit(x, y)


def predict_price(target_year):
    pred = linreg.predict(np.array([target_year]).reshape(-1, 1))
    return pred[0]


def write_output(data):
    with open(output_path, 'w') as f:
        f.write(json.dumps(data))


def execute():
    print(datetime.now().isoformat(), "Model execution started")
    input_data = read_data()
    date = input_data['date']
    data_packages = input_data['data_packages']
    hist_pricing_data = input_data['hist_pricing_data']

    df_hist_pricing_data = pd.DataFrame(data=hist_pricing_data)

    print(datetime.now().isoformat(), "Fitting regression model...")
    train(df_hist_pricing_data)

    year = int(date.split('-')[0])

    print(datetime.now().isoformat(), "Predicting...")
    predicted_price = predict_price(year)

    pred_packages = []
    for data_package in data_packages:
        target_quota = data_package['quota'] + randrange(-1000, 1000)
        package = {
            'draft_package_id': data_package['package_id'],
            'price': int(predicted_price * (target_quota / 1024)),
            'quota': target_quota
        }
        pred_packages.append(package)

    print(datetime.now().isoformat(), "Model executed!")
    write_output(pred_packages)


if __name__ == '__main__':
    execute()
