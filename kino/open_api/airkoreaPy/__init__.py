import json
import requests

class AirKorea(object):

    def __init__(self, token):
        self.token = token
        self.base_url = "http://openapi.airkorea.or.kr/openapi/services/rest"

    def forecast(self, stationName):
        resource_path = "/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty?"
        params = "stationName=" + stationName + "&dataTerm=daily&pageNo=1&numOfRows=1&ServiceKey=" + self.token + "&ver=1.3&_returnType=json"
        r = requests.get(self.base_url + resource_path + params)

        if r.status_code == 200:
            return self.__convert_response(r.text)
        else:
            return "error"

    def __convert_response(self, response):
        response = json.loads(response)
        if ('list' not in response) or (len(response['list']) == 0):
            return "not_exist"

        r = response['list'][0]
        return {
            "datetime": r['dataTime'],
            "mangName": r['mangName'],
            "cai": {
                "description": "통합지수",
                "value": r['khaiValue'],
                "grade": r['khaiGrade'],
                "unit": ""
            },
            "so2": {
                "description": "아황산가스",
                "value": r['so2Value'],
                "grade": r['so2Grade'],
                "unit": "ppm"
            },
            "co": {
                "description": "일산화탄소",
                "value": r['coValue'],
                "grade": r['coGrade'],
                "unit": "ppm"
            },
            "no2": {
                "description": "이산화질소",
                "value": r['no2Value'],
                "grade": r['no2Grade'],
                "unit": "ppm"
            },
            "o3": {
                "description": "오존",
                "value": r['o3Value'],
                "grade": r['o3Grade'],
                "unit": "ppm"
            },
            "pm10": {
                "description": "미세먼지(pm10)",
                "value": r['pm10Value'],
                "grade": r['pm10Grade'],
                "unit": "ug/m3"
            },
            "pm25": {
                "description": "미세먼지(pm25)",
                "value": r['pm25Value'],
                "grade": r['pm25Grade'],
                "unit": "ug/m3"
            }
        }

