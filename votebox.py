import datetime
from restaurant_votes import RestaurantVotes


class VoteBox(object):
    all_restaurant_votes = {}

    def __init__(self, menu):
        for (order, restaurant_name) in menu.items():
            self.init_restaurant_votes(restaurant_name, order)
            # used so that vote can be reseted every day
            self.date_initialized = datetime.date.today()
            # users_voted used to prevent users from voting twice
            self.users_voted = []

    def vote(self, selection, user):
        if selection == -1:  #reset user's vote
            if self.users_voted.__contains__(user):
                self.users_voted.remove(user)
            self.reset_user_vote_in_restaurants(user)
            return True
        if user in self.users_voted:
            print("user already voted")
            return False
        restaurant_votes = self.all_restaurant_votes.get(selection)
        restaurant_votes.add_vote_for_user(user)
        self.users_voted.append(user)
        print("vote accepted")
        return True

    def is_valid_for(self, date):
        return self.date_initialized == date

    def init_restaurant_votes(self, restaurantName, order):
        self.all_restaurant_votes[order] = RestaurantVotes(restaurantName, order=order)

    def votes_to_string(self):
        text = ""
        for (index, restaurant_votes) in self.all_restaurant_votes.items():
            text += restaurant_votes.restaurantName + "(" + str(index) + "): " + str(restaurant_votes.numberOfVotes) + " votes\n"
        return text

    def blame_to_string(self):
        text = ""
        for (index, restaurant_votes) in self.all_restaurant_votes.items():
            text += restaurant_votes.restaurantName + ": " + restaurant_votes.voters_to_string() + " \n"
        return text

    def reset_user_vote_in_restaurants(self, user):
        for (index, restaurant_votes) in self.all_restaurant_votes.items():
            restaurant_votes.reset_vote(user)
