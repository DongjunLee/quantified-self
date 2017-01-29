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
        self.location = geolocator.geocode(utils.Profile().get_location())

        api_key = self.config.open_api['dark_sky']['TOKEN']
        lat = self.location.latitude
        lon = self.location.longitude
        self.forecastio = forecastio.load_forecast(api_key, lat, lon)

    def read(self, timely='current'):
        if timely == 'current':
            currently = self.forecastio.currently()
            self.__forecast(currently, timely)
        elif timely == 'daily':
            hourly = self.forecastio.hourly()
            self.__forecast(hourly, timely)
        elif timely == 'weekly':
            daily = self.forecastio.daily()
            self.__forecast(daily, timely)

    def __forecast(self, forecast, timely):

        address = self.location.address
        icon = forecast.icon
        summary = forecast.summary

        if timely == 'current':
            temperature = forecast.temperature
            fallback = summary + " " + str(temperature) + "도"
        else:
            temperature = None
            fallback = summary

        attachments = self.template.make_weather_template(address, icon, summary, temperature=temperature, fallback=fallback)
        self.slackbot.send_message(attachments=attachments)

