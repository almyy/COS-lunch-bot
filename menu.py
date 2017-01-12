import datetime
from menu_item import MenuItem

class Menu(object):

    def __init__(self):
        self.menuItems = []
        self.cacheTimestamp = datetime.date.today()

    def add_menu_item(self, itemName, itemValue, order):
        menuItem = MenuItem(itemName, itemValue, order)
        self.menuItems.append(menuItem)

    def get_menu(self):
        return sorted(self.menuItems, key=MenuItem.get_key)

    def is_menu_valid(self, date):
        return self.cacheTimestamp == date.today()

    @classmethod
    def from_json(cls, result):
        menu = cls()
        for r in result['results']:
            if r['restaurant']['objectId'] == 'vhYbt71R5s':
                menu.add_menu_item('Eat the street', r['lunchMenuEN'], 0)
            elif r['restaurant']['objectId'] == 'bzQ7G5WKro':
                menu.add_menu_item('Fresh 4 you', r['lunchMenuEN'], 1)
            elif r['restaurant']['objectId'] == 'tnaU8GppPK':
                menu.add_menu_item('Soup and sandwich', r['lunchMenuEN'], 2)
        return menu
