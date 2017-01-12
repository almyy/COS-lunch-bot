# Class representing single restaurant with number of votes
# for that day and all the users that voted
class RestaurantVotes:
    def __init__(self, restaurantName=None, order=None):
        self.restaurantName = restaurantName
        self.order = order
        self.numberOfVotes = 0
        #users_voted used for blame function :)
        self.users_voted = []

    def add_vote_for_user(self, user):
        self.numberOfVotes += 1
        self.users_voted.append(user)

    def voters_to_string(self):
        text = ""
        for user in self.users_voted:
            text = text + "<@{}>".format(user) + ", "
        if text.__eq__(""):
            return "None"
        return text[:-2]

    def get_key(self):
        return self.order

    def __cmp__(self, other):
        if hasattr(other, 'getKey'):
            return self.getKey().__cmp__(other.getKey())

    def reset_vote(self, user):
        if self.users_voted.__contains__(user):
            self.users_voted.remove(user)
            self.numberOfVotes -= 1
