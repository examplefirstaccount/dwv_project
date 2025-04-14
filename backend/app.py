import os

import pandas as pd
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from data_processor import TemperatureDataProcessor

app = Flask(__name__)
CORS(app)
IMAGE_DIR = 'data/heatmaps'


@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, Weather Visualization!"})


@app.route('/api/mean_temperature/<int:start_year>/<int:end_year>')
def mean_temperature(start_year, end_year):
    processor = TemperatureDataProcessor()
    try:
        df = processor.get_mean_temperature_by_year(start_year, end_year)
        return jsonify({
            'years': df['year'].tolist(),
            'temperatures': df['mean_temp'].tolist()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        processor.close()


@app.route('/api/country_temperature/<country>/<int:start_year>/<int:end_year>')
def country_temperature(country, start_year, end_year):
    processor = TemperatureDataProcessor()
    try:
        df = processor.get_mean_temperature_by_year(start_year, end_year, country)
        return jsonify({
            'years': df['year'].tolist(),
            'temperatures': df['mean_temp'].tolist()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        processor.close()


@app.route('/api/countries')
def get_countries():
    processor = TemperatureDataProcessor()
    try:
        countries = processor.get_countries_list(eu_only=True)
        return jsonify(countries)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        processor.close()


@app.route('/api/extreme_countries_temperatures/<int:start_year>/<int:end_year>')
def extreme_countries_temperatures(start_year, end_year):
    processor = TemperatureDataProcessor()
    try:
        df = processor.get_extreme_countries_temperatures(start_year, end_year)
        return jsonify(df)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        processor.close()


@app.route('/api/heatmap_data')
def get_heatmap_data():
    processor = TemperatureDataProcessor()
    try:
        df = processor.get_heatmap_data()
        return jsonify(df)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        processor.close()


@app.route('/api/heatmap')
def get_heatmap():
    year = int(request.args.get('year', 2020))
    image_path = os.path.join(IMAGE_DIR, f'heatmap_{year}.png')
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    else:
        return {'error': 'Year out of range or not found'}, 400


@app.route('/api/precipitation')
def get_mean_precipitation():
    country = request.args.get('country')
    year = int(request.args.get('year', 2020))
    processor = TemperatureDataProcessor()
    try:
        df = processor.get_all(year, country)
        df['precipitation'] = pd.to_numeric(df['precipitation'], errors='coerce')
        df.dropna(inplace=True)
        grouped = df.groupby("date").mean()
        return jsonify(grouped.to_dict(orient="index"))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        processor.close()

@app.route('/api/min_max')
def get_min_max():
    month = int(request.args.get('month', 1))
    start_year = int(request.args.get('start_year', 2020))
    end_year = int(request.args.get('end_year', 2020))
    processor = TemperatureDataProcessor()
    try:
        df = processor.get_monthly_extremes_by_year(month, start_year, end_year)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        processor.close()




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)