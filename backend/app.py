from flask import Flask, jsonify
from flask_cors import CORS

from data_processor import TemperatureDataProcessor

app = Flask(__name__)
CORS(app)


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


if __name__ == '__main__':
    app.run(debug=True)