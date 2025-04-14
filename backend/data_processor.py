import numpy as np
import pandas as pd
from sqlalchemy import create_engine


class TemperatureDataProcessor:
    def __init__(self, database_url="sqlite:///data/weather_eu.db"):
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

    def get_heatmap_data(self):
        eu_countries = self.get_countries_list(eu_only=True)

        query = """
        SELECT 
            s.id,
            s.country,
            s.latitude,
            s.longitude,
            strftime('%Y', w.date) as year,
            AVG(w.temperature_avg) as temperature_avg
        FROM weather w
        JOIN stations s ON w.station_id = s.id
        WHERE s.country IN ({europe})
          AND strftime('%Y', w.date) BETWEEN '1950' AND '2020'
        GROUP BY s.id, year
        ORDER BY year, s.country
        """.format(
            europe=','.join([f"'{c}'" for c in eu_countries])
        )

        df = pd.read_sql_query(query, self.engine)
        df['temperature_avg'] = df['temperature_avg'].replace({np.nan: None}).round(2)
        df['year'] = df['year'].astype(int)

        result = {
            year: group.drop(columns=['year'])
            .to_dict('records')
            for year, group in df.groupby('year')
        }

        return result

    def get_monthly_extremes_by_year(self, month, start_year, end_year, country=None):
        """
        Get min and max temperatures for a specific month over a range of years
        """
        query = """
        SELECT 
            strftime('%Y', w.date) AS year,
            MIN(w.temperature_avg) AS min_temp,
            MAX(w.temperature_avg) AS max_temp
        FROM weather w
        JOIN stations s ON w.station_id = s.id
        WHERE strftime('%m', w.date) = :month
          AND strftime('%Y', w.date) BETWEEN :start AND :end
          {country_filter}
        GROUP BY year
        ORDER BY year
        """.format(
            country_filter="AND s.country = :country" if country else ""
        )
    
        params = {
            'month': f"{int(month):02d}",
            'start': str(start_year),
            'end': str(end_year),
        }
        if country:
            params['country'] = country
    
        df = pd.read_sql_query(query, self.engine, params=params)
        df['year'] = df['year'].astype(int)
        df['min_temp'] = df['min_temp'].round(2)
        df['max_temp'] = df['max_temp'].round(2)
        return df

    def get_all(self, year, country):
        query = """
        SELECT date, precipitation
        FROM weather w
        JOIN stations s ON w.station_id = s.id
        WHERE s.country = ? AND strftime('%Y', w.date) = ?
        """
        df = pd.read_sql_query(
            query,
            self.engine,
            params=(country, str(year))  # year нужно преобразовать в строку для strftime
        )
        return df

    def close(self):
        """Clean up resources"""
        self.engine.dispose()
