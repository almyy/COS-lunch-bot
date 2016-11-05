import requests
import os
import datetime
import json
import time
from slackclient import SlackClient
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def get_bot_id():
    bot_name = 'lunchbot'
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == bot_name:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
                return user.get('id')
    else:
        print("could not find bot user with the name " + bot_name)
    return None


def parse_slack_output(slack_rtm_output, bot_id):
    at_bot = "<@" + bot_id + ">"
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and at_bot in output['text']:
                return output['text'].split(at_bot)[1].strip().lower(), output['channel']
    return None, None


def parse_menu_json(menus):
    res_obj = {}
    for r in menus['results']:
        if r['restaurant']['objectId'] == 'vhYbt71R5s':
            res_obj['Eat the street'] = r['lunchMenuEN']
        elif r['restaurant']['objectId'] == 'tnaU8GppPK':
            res_obj['Soup and sandwich'] = r['lunchMenuEN']
        elif r['restaurant']['objectId'] == 'bzQ7G5WKro':
            res_obj['Fresh 4 you'] = r['lunchMenuEN']
    return res_obj


def find_menu():
    today = datetime.date.today()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    if today.weekday() == 5 or today.weekday() == 6:
        return None

    json_obj = {
        "where": {
            "date": {
                "$gte": {
                    "__type": "Date",
                    "iso": today.isoformat()
                },
                "$lte": {
                    "__type": "Date",
                    "iso": tomorrow.isoformat()
                }
            }
        },
        "_method": "get"
    }
    headers = {
        "X-Parse-Application-Id": "nAixMGyDvVeNfeWEectyJrvtqSeKregQs2gLh9Aw"
    }
    res = requests.post("http://lunch-menu.herokuapp.com/parse/classes/Menu", json=json_obj, headers=headers)
    return parse_menu_json(res.json())


def handle_command(command, channel):
    attachments = []
    if "lunch" in command:
        menus = find_menu()
        if menus is None:
            attachments.append({
                "title": "NO LUNCH IN THE WEEKEND, FOOL!",
                "text": "Stupid...",
                "fallback": "There's no lunch on weekends, stupid"
            })
        else:
            for (key, value) in menus.items():
                attachments.append({
                    "title": key,
                    "text": value,
                    "fallback": key + " - " + value,
                    "color": "good"
                })
    else:
        attachments.append({
            "title": "Too dumb",
            "text": "I'm not smart enough to understand that. Try something with lunch",
            "fallback": "That's not a command"
        })
    slack_client.api_call("chat.postMessage", channel=channel, as_user=True, attachments=attachments)


if __name__ == "__main__":
    bot_id = get_bot_id()
    if bot_id is not None:
        if slack_client.rtm_connect():
            print("lunchbot connected and running!")
            while True:
                command, channel = parse_slack_output(slack_client.rtm_read(), bot_id)
                if command and channel:
                    handle_command(command, channel)
                time.sleep(1)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")
