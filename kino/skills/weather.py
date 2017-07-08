# -*- coding: utf-8 -*-

import arrow
from dateutil import tz
import forecastio
from geopy.geocoders import GoogleV3

from ..open_api.airkoreaPy import AirKorea

from ..slack.slackbot import SlackerAdapter
from ..slack.template import MsgTemplate

from ..utils.config import Config
from ..utils.profile import Profile


class Weather(object):

    def __init__(self, slackbot=None):
        self.config = Config()

        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

    def forecast(self, timely='current'):
        geolocator = GoogleV3()
        location = geolocator.geocode(Profile().get_location())

        api_key = self.config.open_api['dark_sky']['TOKEN']
        lat = location.latitude
        lon = location.longitude
        dark_sky = forecastio.load_forecast(api_key, lat, lon)

        if timely == 'current':
            currently = dark_sky.currently()
            self.__forecast(currently, timely, location.address)
        elif timely == 'daily':
            hourly = dark_sky.hourly()
            self.__forecast(hourly, timely, location.address)
        elif timely == 'weekly':
            daily = dark_sky.daily()
            self.__forecast(daily, timely, location.address)

    def __forecast(self, forecast, timely, address):
        icon = forecast.icon
        summary = forecast.summary

        if timely == 'current':
            temperature = str(forecast.temperature) + "도"
            fallback = summary + " " + temperature
        else:
            temperature = self.__hourly_temperature(forecast)
            fallback = summary + " " + temperature

        attachments = MsgTemplate.make_weather_template(
            address, icon, summary, temperature=temperature, fallback=fallback)
        self.slackbot.send_message(attachments=attachments)

    def __hourly_temperature(self, forecast):
        hourly_temp = []
        h = forecast.data
        for i in range(0, 24, 3):
            time = arrow.get(
                h[i].d['time'],
                tzinfo=tz.tzlocal()).format('D일 H시')
            temperature = h[i].d['temperature']
            hourly_temp.append("- " + time + ": " + str(temperature) + "도")
        hourly_temp = "\n".join(hourly_temp)
        return hourly_temp

    def air_quality(self):
        api_key = self.config.open_api['airkorea']['TOKEN']
        airkorea = AirKorea(api_key)

        station_name = Profile().get_location(station=True)
        response = airkorea.forecast(station_name)
        attachments = MsgTemplate.make_air_quality_template(
            station_name, response)
        self.slackbot.send_message(attachments=attachments)
