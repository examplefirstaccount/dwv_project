import pandas as pd
from sqlalchemy import create_engine


class TemperatureDataProcessor:
    def __init__(self, database_url="sqlite:///weather_data.db"):
        self.engine = create_engine(database_url)

    def get_mean_temperature_by_year(self, start_year, end_year):
        """
        Calculate mean annual temperature for Europe across specified years
        Returns: DataFrame with 'year' and 'mean_temp' columns
        """
        query = """
        SELECT 
            strftime('%Y', w.date) as year,
            AVG(w.temperature_avg) as mean_temp
        FROM weather w
        JOIN stations s ON w.station_id = s.id
        WHERE year BETWEEN :start AND :end
        AND s.country != 'RU'
        GROUP BY year
        ORDER BY year
        """

        df = pd.read_sql_query(
            query,
            self.engine,
            params={'start': str(start_year), 'end': str(end_year)}
        )

        # Data processing
        df['year'] = df['year'].astype(int)
        df['mean_temp'] = df['mean_temp'].round(2)

        return df

    def close(self):
        """Clean up resources"""
        self.engine.dispose()
