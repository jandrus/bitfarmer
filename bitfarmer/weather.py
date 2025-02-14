#!/usr/bin/env python3

import json
from dataclasses import dataclass
from typing import Tuple

import requests

import bitfarmer.coloring as coloring

TEMP_HOT_C = 33
TEMP_WARN_C = 25
TEMP_HOT_F = 91
TEMP_WARN_F = 77
WEATHER_ERROR_MSG = coloring.warn_color("Weather unavailable")


@dataclass
class Weather:
    metric: bool
    temp: int
    real_feel: int
    humidity: int
    precipitation: float
    wind: int
    wind_dir: str
    desc: str
    area: str
    region: str
    country: str

    def csv(self) -> str:
        if self.metric:
            return f"{self.desc}, {self.temp}C, {self.real_feel}C, {self.humidity}%, {self.precipitation}mm, {self.wind}kmph, {self.wind_dir}, {self.country}, {self.region}, {self.area}"
        return f"{self.desc}, {self.temp}F, {self.real_feel}F, {self.humidity}%, {self.precipitation}In, {self.wind}mph, {self.wind_dir}, {self.country}, {self.region}, {self.area}"

    def csv_header(self) -> str:
        if self.metric:
            return "TIMESTAMP, DESCRIPTION, TEMPERATURE (C), REAL_FEEL (C), HUMIDITY (%), PRECIPITATION (mm), WIND (kmph), WIND_DIRECTION, COUNTRY, REGION, AREA\n"
        return "TIMESTAMP, DESCRIPTION, TEMPERATURE (F), REAL_FEEL (F), HUMIDITY (%), PRECIPITATION (in), WIND (mph), WIND_DIRECTION, COUNTRY, REGION, AREA\n"

    def is_hot(self) -> bool:
        if self.metric:
            return self.temp >= TEMP_HOT_C
        return self.temp >= TEMP_HOT_F

    def is_warm(self) -> bool:
        if self.metric:
            return self.temp >= TEMP_WARN_C
        return self.temp >= TEMP_WARN_F

    def __str__(self):
        location = coloring.success_color(f"{self.area} {self.region}")
        if self.metric:
            s = f" [{self.desc}] Temp {self.temp}C (Feels Like {self.real_feel}C), Precip {self.precipitation}mm,  Wind {self.wind}kmph ({self.wind_dir}), Humidity {self.humidity}%"
        else:
            s = f" [{self.desc}] Temp {self.temp}F (Feels Like {self.real_feel}F), Precip {self.precipitation}in, Wind {self.wind}mph ({self.wind_dir}), Humidity {self.humidity}%"
        if self.is_hot():
            s = coloring.err_color(s)
        elif self.is_warm():
            s = coloring.warn_color(s)
        else:
            s = coloring.primary_color(s)
        return location + s


def get_weather(conf: dict) -> Weather:
    """Get current parameters"""
    wtr = get_weather_json(conf)
    area, region, country = get_location(wtr)
    temp = int(
        wtr["current_condition"][0]["temp_C"]
        if conf["weather"]["metric"]
        else wtr["current_condition"][0]["temp_F"]
    )
    real_feel = int(
        wtr["current_condition"][0]["FeelsLikeC"]
        if conf["weather"]["metric"]
        else wtr["current_condition"][0]["FeelsLikeF"]
    )
    precipitation = float(
        wtr["current_condition"][0]["precipMM"]
        if conf["weather"]["metric"]
        else wtr["current_condition"][0]["precipInches"]
    )
    wind = int(
        wtr["current_condition"][0]["windspeedKmph"]
        if conf["weather"]["metric"]
        else wtr["current_condition"][0]["windspeedMiles"]
    )
    return Weather(
        conf["weather"]["metric"],
        temp,
        real_feel,
        int(wtr["current_condition"][0]["humidity"]),
        precipitation,
        wind,
        wtr["current_condition"][0]["winddir16Point"],
        wtr["current_condition"][0]["weatherDesc"][0]["value"],
        area,
        region,
        country,
    )


def get_weather_json(conf: dict) -> dict:
    """Get weather json"""
    area = conf["weather"]["area"].replace(" ", "+")
    region = conf["weather"]["region"].replace(" ", "+")
    country = conf["weather"]["country"].replace(" ", "+")
    resp = requests.get(f"http://wttr.in/{area}+{region}+{country}?&format=j2")
    if resp.status_code != requests.codes.ok:
        resp.raise_for_status()
    return json.loads(resp.text)


def get_location(wtr: dict) -> Tuple[str, str, str]:
    """Get location weather is being pulled from"""
    area = wtr["nearest_area"][0]["areaName"][0]["value"]
    country = wtr["nearest_area"][0]["country"][0]["value"]
    region = wtr["nearest_area"][0]["region"][0]["value"]
    return (area, region, country)


if __name__ == "__main__":
    conf = {
        "weather": {
            "metric": False,
            "area": "Rocky Mount",
            "region": "North Carolina",
            "country": "United States",
        }
    }
    # get_location(conf)
    weather = get_weather(conf)
    print(weather)
