import re

class InverseRelation():
    INVERSE_RELATION_PATTERN = r'(\s*(?:SELF\\)?(?:(?:\w+\.)?)+\w+(?:\s+RENAMED\s+\w+)?\s*:\s*(?:OPTIONAL\s+)?(?:(?:(?:SET)|(?:BAG))\s+(?:\[\d+:(?:\d+|\?)\]\s+)?OF\s+\w+\s+FOR\s+\w+\s*;))'

    def __init__(self, txt):
        self.txt = txt