# -*- coding: utf-8 -*-

class MsgTemplate(object):

    def __init__(self):
        pass

    def make_schedule_template(self, pretext, data):
        attachments = []
        for k,v in data.items():
            if k == "index":
                continue

            a_dict = dict()

            if pretext == "":
                pass
            else:
                a_dict['pretext'] = pretext

            a_dict['title'] = "index: " + k
            a_dict['fallback'] = "알람에서 변경이 있습니다."

            if 'color' in v:
                a_dict['color'] = v['color']
                v.pop('color', None)
            else:
                a_dict['color'] = "#438C56"

            text = ""
            for d_k,d_v in v.items():
                if type(d_v) == type([]):
                    text += " - " + d_k + "\n"
                    for element in d_v:
                        text += " - - " + element + "\n"
                else:
                    text += " - " + d_k + ": " + d_v + "\n"
            a_dict['text'] = text

            a_dict['mrkdwn_in'] = ["text", "pretext"]


            attachments.append(a_dict)
        return attachments

