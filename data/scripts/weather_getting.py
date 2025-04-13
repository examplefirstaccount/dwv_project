from datetime import datetime, timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup

from db_operations import create_data_base, create_table, insert_into_db
from weather_station_scraper import get_station_codes


def get_country_codes():
    countries = {}
    bs = BeautifulSoup(requests.get("http://pogoda-service.ru/archive_gsod.php").content, "html.parser")
    for select_tag in bs.find_all("select"):
        if select_tag.get("id") == "country":
            for option in select_tag.find_all("option")[1:]:
                country = option.text.strip()
                code = option.get("value").strip()
                countries[country] = code
    return countries


def extract_temperature(country_code, station_code, time_beg, time_end):
    # Указываем URL страницы
    url = "http://pogoda-service.ru/archive_gsod_res.php"

    # Параметры запроса
    payload = {
        "country": country_code,  # Код страны
        "station": station_code,  # Код метеостанции
        "datepicker_beg": time_beg,  # Начальная дата
        "datepicker_end": time_end  # Конечная дата
    }

    # Отправляем GET-запрос с параметрами
    response = requests.get(url, params=payload)
    response.encoding = 'utf-8'

    date_ind, temper_ind = [0, 3]  # индексы колонок даты и средней температуры в таблицы
    # Проверяем успешность запроса
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table")
        ls = []
        last_date = None

        if table:
            for row in table.find_all("tr"):
                cols = [col.text.strip() for col in row.find_all("td")]
                if cols:
                    ls.append([".".join(cols[date_ind].split(".")[1:]), cols[temper_ind], 1])
                    last_date = cols[date_ind]
            if ls:
                last_month = ".".join(last_date.split(".")[1:])

                df = pd.DataFrame(data=ls, columns=["date", "mean_temperature", "number_of_days"])
                days_in_last_month = int(df["date"].value_counts()[last_month])
                df["mean_temperature"] = df["mean_temperature"].astype("float")
                df = df.groupby("date").agg({"mean_temperature": "mean", "number_of_days": "sum"}).reset_index()

                last_month_info = df[df["date"] == last_month]
                mean_weather = float(last_month_info["mean_temperature"].iloc[0])

                df.drop(last_month_info.index, inplace=True)
                return df, last_date, days_in_last_month, mean_weather
        else:
            print("Данные не найдены")
        return None

    else:
        print(f"Ошибка запроса: {response.status_code}")


def update_date(date):
    date = datetime.strptime(date, "%d.%m.%Y")
    date += timedelta(days=1)
    return date.strftime("%d.%m.%Y")


create_data_base()


country_codes = get_country_codes()
for country in country_codes:
    create_table(country)
    station_codes = get_station_codes(country)
    for station in station_codes:
        beg = "01.01.1930"
        end = "31.12.2024"
        station_temperature = extract_temperature(country_codes[country], station_codes[station], time_beg=beg,
                                                  time_end=end)

        while station_temperature is not None:
            weather_data, date, days_num, mean_temp = station_temperature
            insert_into_db(country, station, weather_data.iloc[:, :2])

            beg = update_date(date)
            station_temperature = extract_temperature(country_codes[country], station_codes[station], time_beg=beg,
                                                      time_end=end)

            if station_temperature is not None:
                df = station_temperature[0]
                last_month = ".".join(date.split(".")[1:])
                last_month_info = df[df["date"] == last_month]

                last_month_info.loc[:, "mean_temperature"] = (
                        (last_month_info["mean_temperature"].values * last_month_info[
                            "number_of_days"].values + mean_temp * days_num) /
                        (last_month_info["number_of_days"].values + days_num)
                )
            else:
                data = [[".".join(date.split(".")[1:]), mean_temp]]
                insert_into_db(country, station, pd.DataFrame(data=data))
    break
