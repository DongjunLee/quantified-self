# -*- coding: utf-8 -*-

import datetime
import forecastio
from geopy.geocoders import GoogleV3

from kino.template import MsgTemplate
from slack.slackbot import SlackerAdapter
from utils.config import Config

class Weather(object):

    def __init__(self):
        self.config = Config()
        self.slackbot = SlackerAdapter()
        self.template = MsgTemplate()

        geolocator = GoogleV3()
        self.location = geolocator.geocode(self.config.weather["HOME"])

        api_key = self.config.weather["DARK_SKY_SECRET_KEY"]
        lat = self.location.latitude
        lon = self.location.longitude
        self.forecastio = forecastio.load_forecast(api_key, lat, lon)

    def read(self, channel=None, when='current'):
        if when == 'current':
            self.__current_forecast(channel=channel)
        elif when == 'daily':
            self.__daily_forecast(channel=channel)

    def __daily_forecast(self, channel=None):
        daily = self.forecastio.daily()

        address = self.location.address
        icon = daily.icon
        summary = daily.summary

        attachments = self.template.make_weather_template(address, icon, summary)
        self.slackbot.send_message(channel=channel, attachments=attachments)

    def __current_forecast(self, channel=None):
        current = self.forecastio.currently()

        address = self.location.address
        icon = current.icon
        summary = current.summary
        temperature = current.temperature

        attachments = self.template.make_weather_template(address, icon, summary, temperature=temperature)
        self.slackbot.send_message(channel=channel, attachments=attachments)


