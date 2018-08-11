import json
import requests
import xml.etree.ElementTree as ET
from xmljson import yahoo as yh

from hbconfig import Config

from ..slack.resource import MsgResource
from ..slack.template import MsgTemplate
from ..slack.slackbot import SlackerAdapter

from ..utils.data_handler import DataHandler


class Bus(object):
    def __init__(self, slackbot=None):
        self.data_handler = DataHandler()

        self.ansan_bus = self.data_handler.read_file("ansan_bus.json")
        self.ansan_station = self.data_handler.read_file("ansan_station.json")
        self.service_key = Config.open_api.gbis.TOKEN

        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

    def arrive_info(self, station_id, real_time=False):
        url = "http://openapi.gbis.go.kr/ws/rest/busarrivalservice/station?"
        url += "serviceKey=" + self.service_key + "&stationId=" + station_id

        req_json = self.__request(url)
        try:
            result = {}
            bus_list = req_json["response"]["msgBody"]["busArrivalList"]
            for b in bus_list:
                bus_number = self.get_bus_number(b["routeId"])
                location1 = b["locationNo1"]
                predict1 = b["predictTime1"]

                location2 = b["locationNo2"]
                predict2 = b["predictTime2"]

                if bus_number == -1:
                    continue

                bus1 = ""
                if location1 == {}:
                    bus1 += "도착 정보가 없습니다."
                else:
                    bus1 += str(location1) + "번째 전 전류장 (" + str(predict1) + "분)"
                bus2 = ""
                if location2 == {}:
                    bus2 += "도착 정보가 없습니다."
                else:
                    bus2 += str(location2) + "번째 전 전류장 (" + str(predict2) + "분)"

                result[bus_number] = {"bus1": bus1, "bus2": bus2}
        except BaseException:
            self.slackbot.send_message(text=MsgResource.ERROR)

        attachments = MsgTemplate.make_bus_stop_template(result)
        if real_time:
            self.slackbot.update_message(attachments=attachments)
        else:
            self.slackbot.send_message(attachments=attachments)

    def __request(self, url):
        req = requests.get(url)

        response = req.text
        response = response[response.index("<response>") :]

        res_json = json.dumps(yh.data(ET.fromstring(response)))
        return json.loads(res_json)

    def get_station_id(self, name):
        pass

    def get_bus_number(self, route_id):
        return self.ansan_bus.get(route_id, {}).get("ROUTE_NM", -1)
