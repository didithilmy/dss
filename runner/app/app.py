import json
import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
import settings

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.DB_URL
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


def get_data_packages():
    results = []
    result = db.session.execute("SELECT * FROM data_package")
    for r in result:
        results.append(dict(r.items()))
    return results


def get_region():
    results = []
    result = db.session.execute("SELECT * FROM region")
    for r in result:
        results.append(dict(r.items()))
    return results


def get_region_by_code(region_code):
    results = []
    result = db.session.execute(
        "SELECT * FROM region WHERE region_code = ':region_code'", {'region_code': region_code})
    for r in result:
        results.append(dict(r.items()))
    return results[0]


def do_inference(region_code, date):
    hist_pricing_data = get_historical_pricing_data(region_code)
    data_packages = get_data_packages()

    data = {
        'hist_pricing_data': hist_pricing_data,
        'data_packages': data_packages,
        'date': date
    }

    r = requests.post(settings.MBMS_URL + '/models/determine_packages/run/', json=data)
    r_data = r.json()

    r_output = r_data['output']
    rec_entities = []
    for rec in r_output:
        price = rec['price']
        quota = rec['quota']
        draft_package_id = rec['draft_package_id']
        rec_entity = PackageRecommendation(
            date=date, region_code=region_code, price=price, quota=quota, draft_package_id=draft_package_id)

        try:
            db.session.add(rec_entity)
            db.session.commit()
        except:
            db.session.rollback()
            print("Duplicate key, skipping...")

        rec_entities.append(dict(date=date, region_code=region_code,
                                 price=price, quota=quota, draft_package_id=draft_package_id))
    return rec_entities


@app.route('/')
def home():
    regions = get_region()
    return render_template('index.html', regions=regions)


@app.route('/infer', methods=['POST'])
def infer():
    region_code = int(request.form['region_code'])
    date = request.form['date']

    result = do_inference(region_code, date)
    region = get_region_by_code(region_code)

    return render_template('result.html', result=result, region=region, date=date)
