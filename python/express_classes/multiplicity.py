import re

class Multiplicity:
    MIN_PATTERN = r'(?:(?:SET)|(?:BAG))\s+\[(\d+):(?:\d+|\?)\]\s+OF\s+'
    MAX_PATTERN = r'(?:(?:SET)|(?:BAG))\s+\[\d+:(\d+)\]\s+OF\s+'

    def __init__(self, txt, relation):
        self.txt = txt
        self.relation = relation
        self._get_minimum()
        self._get_maximum()
        self._get_bag()
        self._get_set()
    
    def _get_minimum(self):
        match = re.match(self.MIN_PATTERN, self.txt)
        if match:
            self.minimum = int(match.group(1))
        else:
            print("Couldn't find a minimum in the following text:\n" + self.txt)

    def _get_maximum(self):
        match = re.match(self.MAX_PATTERN, self.txt)
        if match:
            self.has_maximum = True
            self.maximum = int(match.group(1))
        else:
            self.has_maximum = False

    def _get_bag(self):
        self.is_bag = "BAG" in self.txt

    def _get_set(self):
        self.is_set = "SET" in self.txt