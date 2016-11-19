# -*- coding: utf-8 -*-

import datetime
import forecastio
from geopy.geocoders import GoogleV3

import slack
import utils

class Weather(object):

    def __init__(self, text=None):
        self.input = text
        self.config = utils.Config()
        self.slackbot = slack.SlackerAdapter()
        self.template = slack.MsgTemplate()

        geolocator = GoogleV3()
        self.location = geolocator.geocode(self.config.weather["HOME"])

        api_key = self.config.weather["DARK_SKY_SECRET_KEY"]
        lat = self.location.latitude
        lon = self.location.longitude
        self.forecastio = forecastio.load_forecast(api_key, lat, lon)

    def read(self, timely='current'):
        if timely == 'current':
            self.__current_forecast()
        elif timely == 'daily':
            self.__daily_forecast()

    def __daily_forecast(self, channel=None):
        daily = self.forecastio.daily()

        address = self.location.address
        icon = daily.icon
        summary = daily.summary
        fallback = summary

        attachments = self.template.make_weather_template(address, icon, summary, fallback=fallback)
        self.slackbot.send_message(channel=channel, attachments=attachments)

    def __current_forecast(self, channel=None):
        current = self.forecastio.currently()

        address = self.location.address
        icon = current.icon
        summary = current.summary
        temperature = current.temperature
        fallback = summary + " " + str(temperature) + "도"

        attachments = self.template.make_weather_template(address, icon, summary, temperature=temperature, fallback=fallback)
        self.slackbot.send_message(channel=channel, attachments=attachments)


