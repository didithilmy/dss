import json
import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import settings

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/dss'
db = SQLAlchemy(app)


class PackageRecommendation(db.Model):
    draft_package_id = db.Column(db.String(5), primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    region_code = db.Column(db.String(10), primary_key=True)
    price = db.Column(db.Integer)
    quota = db.Column(db.Integer)

    def __repr__(self):
        return '<PackageRecommendation %r>' % self.draft_package_id


db.create_all()


def get_historical_pricing_data(region_code):
    results = []
    result = db.session.execute(
        "SELECT * FROM historical_pricing_data WHERE region_code = ':region_code'", {'region_code': region_code})
    for r in result:
        results.append(dict(r.items()))
    return results


def get_historical_market_info(region_code):
    results = []
    result = db.session.execute(
        "SELECT * FROM historical_market_info WHERE region_code = ':region_code'", {'region_code': region_code})
    for r in result:
        results.append(dict(r.items()))
    return results


def get_data_packages():
    results = []
    result = db.session.execute("SELECT * FROM data_package")
    for r in result:
        results.append(dict(r.items()))
    return results


def do_inference(region_code, date):
    hist_pricing_data = get_historical_pricing_data(region_code)
    hist_market_info = get_historical_market_info(region_code)
    data_packages = get_data_packages()

    data = {
        'hist_pricing_data': hist_pricing_data,
        'hist_market_info': hist_market_info,
        'data_packages': data_packages,
        'date': date
    }

    r = requests.post(settings.MBMS_URL, json=data)
    r_data = r.json()

    rec_entities = []
    for rec in r_data:
        price = rec['price']
        quota = rec['quota']
        draft_package_id = rec['draft_package_id']
        rec_entity = PackageRecommendation(date=date, region_code=region_code, price=price, quota=quota, draft_package_id=draft_package_id)
        
        db.session.save(rec_entity)
        rec_entities.append(dict(rec_entity))

    return rec_entities

@app.route('/')
def hello_world():
    hist_pricing_data = get_historical_pricing_data(1101)
    hist_market_info = get_historical_market_info(1101)
    data_packages = get_data_packages()
    
    data = {
        'hist_pricing_data': hist_pricing_data,
        'hist_market_info': hist_market_info,
        'data_packages': data_packages,
    }
    return json.dumps(data, default=str)
