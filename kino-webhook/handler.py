import arrow
import json
import requests



def kanban_webhook(event, context):
    input_body = json.loads(event['body'])
    print(event['body'])

    action = input_body["action"]
    action_type = action["type"]

    if action_type == "createCard":
        list_name, card_name = get_create_card(action["data"])
    elif action_type == "updateCard":
        list_name, card_name = get_update_card(action["data"])

    kanban_list = ["DOING", "BREAK", "DONE"]
    if list_name in kanban_list:
        payload = make_payload(action=list_name, msg=card_name)
        r = send_to_kino({"text": payload})

        response = {
            "statusCode": r.status_code
        }

    response = {
        "statusCode": 400
    }
    return response

def get_create_card(action_data):
    list_name = action_data["list"]["name"].upper()
    card_name = action_data["card"]["name"]
    return list_name, card_name

def get_update_card(action_data):
    list_name = action_data["listAfter"]["name"].upper()
    card_name = action_data["card"]["name"]
    return list_name, card_name

def make_payload(action=None, msg=None, time=None):
    if time is None:
        now = arrow.now()
        time = now.format(" MMMM d, YYYY") + " at " + now.format("HH:mmA")
    payload = {
        "action": "KANBAN_" + action,
        "msg": msg,
        "time": time
    }
    return json.dumps(payload)

def send_to_kino(data):
    return requests.post("https://hooks.slack.com/services/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", data=json.dumps(data))
