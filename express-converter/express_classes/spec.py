import re
from .entity import Entity
from collections import defaultdict

class Spec:
    ENTITY_PATTERN = r'(ENTITY(?:(?:[\s\S]*?)*?)END_ENTITY;)'

    def __init__(self, txt):
        self.txt = txt
        entityList = [Entity(match, self) for match in re.findall(Spec.ENTITY_PATTERN, txt)]
        self.entities = {entity.name: entity for entity in entityList}
        self.relations = self._collect_relations()
        self.base_relations = [relation for relation in self.relations if relation.is_redeclared == False]
        #grouped_relations = self._group_relations_by_name()
        #self.print_grouped_relations()
        

    def _collect_relations(self):
        relations = []
        for entity in self.entities.values():
            relations.extend(entity.relations)
        return relations
    
    """
    def _group_relations_by_name(self):
        self.grouped_relations = defaultdict(list)
        for relation in self.relations:
            self.grouped_relations[relation.name].append(relation)
        return self.grouped_relations
    
    def print_grouped_relations(self):
        for name in sorted(self.grouped_relations):
            print(f"Relations for {name}:")
            for relation in self.grouped_relations[name]:
                print(relation.entity.name + " - " + relation.txt)
            print()
    """