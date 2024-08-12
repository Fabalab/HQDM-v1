import re
from .relation import Relation
from .inverse_relation import InverseRelation

class Entity:
    NAME_PATTERN = r'ENTITY\s+(\w+)'
    SUPERTYPE_PATTERN = r'SUBTYPE\s+OF\s*\(\s*((?:\w+\s*(?:,\s*)?)+)\s*\)\s*;'
    RESTRICTED_SUBTYPE_PATTERN = r'SUPERTYPE\s+OF\s+\(\s*ONEOF\s*\((\w+(?:,\s+\w+)*)\s*\)\)'
    RELATION_PATTERN = r'(\s*(?:SELF\\)?(?:(?:\w+\.)?)+\w+(?:\s+RENAMED\s+\w+)?\s*:\s*(?:OPTIONAL\s+)?(?:(?:(?:SET)|(?:BAG))\s+\[\d+:(?:\d+|\?)\]\s+OF\s+)?\w+\s*;)'
    INVERSE_RELATION_PATTERN = r'(\s*(?:SELF\\)?(?:(?:\w+\.)?)+\w+(?:\s+RENAMED\s+\w+)?\s*:\s*(?:OPTIONAL\s+)?(?:(?:(?:SET)|(?:BAG))\s+(?:\[\d+:(?:\d+|\?)\]\s+)?OF\s+\w+\s+FOR\s+\w+\s*;))'
    ABSTRACT_PATTERN = r'ABSTRACT'

    def __init__(self, txt, spec):
        self.txt = txt
        self.spec = spec
        self._get_name()
        self._get_abstract()
        self._get_supertypes()
        self._get_restricted_subtypes()
        self._get_relations()
        self._get_inverse_relations()
        
    def _get_name(self):
        match = re.search(Entity.NAME_PATTERN, self.txt)
        if match:
            self.name = match.group(1)
        else:
            print("No name found within the following text:\n" + self.txt + "\n")

    def _get_abstract(self):
        self.is_abstract = Entity.ABSTRACT_PATTERN in self.txt

    def _get_supertypes(self):
        match = re.search(Entity.SUPERTYPE_PATTERN, self.txt)
        if match:
            self.supertypes = [item.strip() for item in match.group(1).split(',')]
        else:
            self.supertypes = []

    def _get_restricted_subtypes(self):
        match = re.search(Entity.RESTRICTED_SUBTYPE_PATTERN, self.txt)
        if match:
            self.has_restricted_subtypes = True
            self.restricted_subtypes = [item.strip() for item in match.group(1).split(',')]
        else:
            self.has_restricted_subtypes = False
            self.restricted_subtypes = []

    def _get_relations(self):
        lines = self.txt.split("\n")
        self.relations = []
        for line in lines:
            match = re.search(Entity.RELATION_PATTERN, line)
            if(match):
                self.relations.append(Relation(match.group(1), self))

    def _get_inverse_relations(self):
        self.inverse_relations = [InverseRelation(item) for item in re.findall(Entity.INVERSE_RELATION_PATTERN, self.txt)]     