# -*- coding: utf-8 -*-

from utils.resource import MessageResource

class MsgTemplate(object):

    def __init__(self):
        pass

    def make_schedule_template(self, pretext, data):
        attachments = []
        for k,v in data.items():
            if k == "index":
                continue

            a_dict = {}

            if pretext == "":
                pass
            else:
                a_dict['pretext'] = pretext

            a_dict['title'] = "시간대. " + MessageResource.TIMER_ICON + k
            a_dict['fallback'] = "알람에서 변경이 있습니다."

            if 'color' in v:
                a_dict['color'] = v['color']
                v.pop('color', None)
            else:
                a_dict['color'] = "#438C56"

            text = ""
            for d_k,d_v in v.items():
                if type(d_v) == type([]):
                    text += MessageResource.ORANGE_DIAMOND_ICON + d_k + "\n"
                    for element in d_v:
                        text += MessageResource.WHITE_ELEMENT_ICON + element + "\n"
                else:
                    text += MessageResource.ORANGE_DIAMOND_ICON + d_k + ": " + d_v + "\n"
            a_dict['text'] = text

            a_dict['mrkdwn_in'] = ["text", "pretext"]


            attachments.append(a_dict)
        return attachments

    def make_function_template(self, pretext, data):
        attachments = []
        for f_name, f_detail in data.items():

            a_dict = {}
            if pretext == "":
                pass
            else:
                a_dict['pretext'] = pretext

            a_dict['title'] = f_detail["icon"] + f_name
            a_dict['fallback'] = "Function 관련 정보."
            a_dict['color'] = "#438C56"

            text = MessageResource.ORANGE_DIAMOND_ICON + "description: " + f_detail['description'] + "\n"
            text += MessageResource.ORANGE_DIAMOND_ICON + "params" + "\n"
            text += MessageResource.WHITE_ELEMENT_ICON + ", ".join(f_detail['params'])
            a_dict['text'] = text

            a_dict['mrkdwn_in'] = ["text", "pretext"]

            attachments.append(a_dict)
        return attachments



