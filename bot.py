import datetime
import os
import time

import requests
from slackclient import SlackClient

from menu import Menu


class Vote(object):
    users_voted = []
    votes = {}

    def __init__(self, menu):
        for (_, value) in menu.items():
            self.votes[value] = 0

    def vote(self, selection, user):
        if user in self.users_voted:
            print("user already voted")
            return False
        self.votes[selection] += 1
        self.users_voted.append(user)
        print("vote accepted")
        return True


slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
vote = None
index_restaurant = {}
cached_menu = None


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
                return output['text'].split(at_bot)[1].strip().lower(), output['channel'], output['user']
    return None, None, None


def find_menu():
    global cached_menu
    if cached_menu is not None and cached_menu.is_menu_valid(datetime.date.today()):
        return cached_menu
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
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
    cached_menu = Menu.from_json(res.json())
    return cached_menu


def handle_command(command, channel, user):
    global vote
    attachments = []
    if "lunch" in command:
        menus = find_menu()
        if menus is None:
            attachments.append({
                "title": "NO LUNCH IN THE WEEKEND, FOOL!",
                "text": "Stupid...",
                "fallback": "There's no lunch on weekends, stupid",
                "color": "danger"
            })
        else:
            for menu_item in menus.get_menu():
                attachments.append({
                    "title": menu_item.itemName,
                    "text": menu_item.itemValue,
                    "fallback": menu_item.itemName + " - " + menu_item.itemValue,
                    "color": "good"
                })
    elif "vote" in command:
        if vote is None:
            menus = find_menu()
            i = 0
            text = ""
            for key in menus:
                text += "\n" + key + "(" + str(i) + "): 0"
                index_restaurant[i] = key
                i += 1
            vote = Vote(index_restaurant)
            attachments.append({
                "title": "Starting vote...",
                "text": "Tag me with 'vote #', and I'll register your vote!\nExample: @lunchbot vote 1" + text,
                "fallback": "Vote for lunch started",
                "color": "good"
            })
        else:
            # Dirty af
            selection = command.split('vote')[1].split()[0].strip()
            try:
                selection = int(selection)
            except:
                print("Fuck, i broke")
            if vote.vote(index_restaurant[selection], user):
                text = ""
                for (key, value) in vote.votes.items():
                    text += key + ": " + str(value) + " votes\n"
                print(text)
                attachments.append({
                    "title": "Vote",
                    "text": text,
                    "fallback": "Votes are in"
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
                try:
                    command, channel, user = parse_slack_output(slack_client.rtm_read(), bot_id)
                # Fuck it, gotta catch 'em all
                except Exception as e:
                    print("Caught an exception while trying to read:\nReconnecting...", e)
                    slack_client.rtm_connect()
                if command and channel and user:
                    handle_command(command, channel, user)
                time.sleep(1)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")
