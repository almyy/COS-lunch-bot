

class MenuItem:

    def __init__(self, itemName=None, itemValue=None, order = None):
        self.itemName = itemName
        self.itemValue = itemValue
        self.order = order


    def get_key(self):
        return self.order

    def __cmp__(self, other):
        if hasattr(other, 'getKey'):
            return self.getKey().__cmp__(other.getKey())