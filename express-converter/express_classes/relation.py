import re
from .multiplicity import Multiplicity

class Relation:
    NAME_PATTERN = r'\s*(?:SELF\\)?(?:\w+\.)?(\w+)(?:\s+RENAMED\s+\w+)?\s*:\s*(?:OPTIONAL\s+)?(?:(?:(?:SET)|(?:BAG))\s+\[\d+:(?:\d+|\?)\]\s+OF\s+)?\w+\s*;'
    RENAMED_PATTERN = r'\s*(?:SELF\\)?(?:(?:\w+\.)?)+\w+\s+RENAMED\s+(\w+)\s*:\s*(?:OPTIONAL\s+)?(?:(?:(?:SET)|(?:BAG))\s+\[\d+:(?:\d+|\?)\]\s+OF\s+)?\w+\s*;'
    REDECLARED_PATTERN = r'\s*SELF\\(\w+)\.\w+(?:\s+RENAMED\s+\w+)?\s*:\s*(?:OPTIONAL\s+)?(?:(?:(?:SET)|(?:BAG))\s+\[\d+:(?:\d+|\?)\]\s+OF\s+)?\w+\s*;'
    TARGET_PATTERN = r'\s*(?:SELF\\)?(?:(?:\w+\.)?)+\w+(?:\s+RENAMED\s+\w+)?\s*:\s*(?:OPTIONAL\s+)?(?:(?:(?:SET)|(?:BAG))\s+\[\d+:(?:\d+|\?)\]\s+OF\s+)?(\w+)\s*;'
    MULTIPLICITY_PATTERN = r'\s*(?:SELF\\)?(?:(?:\w+\.)?)+\w+(?:\s+RENAMED\s+\w+)?\s*:\s*(?:OPTIONAL\s+)?((?:(?:SET)|(?:BAG))\s+\[\d+:(?:\d+|\?)\]\s+OF\s+)\w+\s*;'

    def __init__(self, txt, entity):
        self.txt = txt
        self.entity = entity
        self._get_name()
        self._get_renamed()
        self._get_redeclared()
        self._is_optional()
        self._get_target()
        self._get_multiplicity()

    def _get_name(self):
        match = re.search(Relation.NAME_PATTERN, self.txt)
        if match:
            self.name = match.group(1)
        else:
            print("No name found within the following text:\n" + self.txt)

    def _get_renamed(self):
        match = re.search(Relation.RENAMED_PATTERN, self.txt)
        if match:
            self.renamed = True
            self.base_name = self.name
            self.name = match.group(1)
        else:
            self.renamed = False

    def _get_redeclared(self):
        match = re.search(Relation.REDECLARED_PATTERN, self.txt)
        if match:
            self.is_redeclared = True
            self.base_class = match.group(1)
        else:
            self.is_redeclared = False

    def _is_optional(self):
        self.is_optional = "OPTIONAL" in self.txt

    def _get_target(self):
        match = re.search(Relation.TARGET_PATTERN, self.txt)
        if match:
            self.target = match.group(1)
        else:
            print("No target found within the following text:\n" + self.txt)

    def _get_multiplicity(self):
        match = re.search(Relation.MULTIPLICITY_PATTERN, self.txt)
        if match:
            self.has_multiplicity = True
            self.multiplicity = Multiplicity(match.group(1), self)
        else:
            self.has_multiplicity = False