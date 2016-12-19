import datetime


class Vote(object):
    users_voted = []
    votes = {}
    date_initialized = {}

    def __init__(self, menu):
        for (_, value) in menu.items():
            self.votes[value] = 0
            self.users_voted = []
            self.date_initialized = datetime.date.today() #used so that vote can be reseted every day

    def vote(self, selection, user):
        if user in self.users_voted:
            print("user already voted")
            return False
        self.votes[selection] += 1
        self.users_voted.append(user)
        print("vote accepted")
        return True

    def is_valid_for(self, date):
        return self.date_initialized == date