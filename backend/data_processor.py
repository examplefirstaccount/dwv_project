import pandas as pd
from sqlalchemy import create_engine


class TemperatureDataProcessor:
    def __init__(self, database_url="sqlite:///weather_eu.db"):
        self.engine = create_engine(database_url)

    def get_mean_temperature_by_year(self, start_year, end_year, country=None):
        """
        Calculate mean annual temperature for Europe or specific country
        """
        query = """
        SELECT 
            strftime('%Y', w.date) as year,
            AVG(w.temperature_avg) as mean_temp
        FROM weather w
        JOIN stations s ON w.station_id = s.id
        WHERE year BETWEEN :start AND :end
        {country_filter}
        GROUP BY year
        ORDER BY year
        """.format(
            country_filter="AND s.country = :country" if country else ""
        )

        params = {'start': str(start_year), 'end': str(end_year)}
        if country:
            params['country'] = country

        df = pd.read_sql_query(
            query,
            self.engine,
            params=params
        )

        # Data processing
        df['year'] = df['year'].astype(int)
        df['mean_temp'] = df['mean_temp'].round(2)

        return df

    def get_extreme_countries_temperatures(self, start_year, end_year):
        hot_countries = ['CY', 'MT', 'GR']
        cold_countries = ['FI', 'IS', 'NO']

        query = """
        SELECT 
            s.country,
            strftime('%Y', w.date) as year,
            AVG(w.temperature_avg) as mean_temp
        FROM weather w
        JOIN stations s ON w.station_id = s.id
        WHERE year BETWEEN :start AND :end
        AND s.country IN ({hot_countries}, {cold_countries})
        GROUP BY s.country, year
        ORDER BY s.country, year
        """.format(
            hot_countries=','.join([f"'{c}'" for c in hot_countries]),
            cold_countries=','.join([f"'{c}'" for c in cold_countries])
        )

        df = pd.read_sql_query(query, self.engine, params={'start': str(start_year), 'end': str(end_year)})

        result = {
            'countries': [],
            'data': {}
        }

        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            result['countries'].append(country)
            result['data'][country] = {
                'years': country_data['year'].astype(int).tolist(),
                'temperatures': country_data['mean_temp'].round(2).tolist(),
                'is_hot': country in hot_countries,
                'avg_temp': country_data['mean_temp'].mean().round(2)
            }

        result['countries'].sort(
            key=lambda x: result['data'][x]['avg_temp'],
            reverse=True
        )

        return result

    def get_countries_list(self, eu_only=False):
        if eu_only:
            eu_countries = ['GR', 'HU', 'BE', 'GI', 'FR', 'JE', 'FI', 'DE', 'LT', 'CY', 'DK', 'MT', 'BY', 'NO', 'SM', 'IT', 'MC', 'RO', 'SK', 'GB', 'NL', 'AT', 'VA', 'PT', 'UA', 'FO', 'HR', 'ME', 'SI', 'BA', 'IM', 'SJ', 'EE', 'IS', 'CH', 'MK', 'GG', 'BG', 'LU', 'AX', 'ES', 'AM', 'CZ', 'IE', 'KZ', 'PL', 'AD', 'LI', 'GE', 'RS', 'TR', 'MD', 'LV', 'AZ', 'SE', 'AL']
            return list(sorted(eu_countries))
        query = "SELECT DISTINCT country FROM stations ORDER BY country"
        df = pd.read_sql_query(query, self.engine)
        return df['country'].sort_values().tolist()

    def close(self):
        """Clean up resources"""
        self.engine.dispose()
