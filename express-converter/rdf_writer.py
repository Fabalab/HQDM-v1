from express_classes import *
from rdflib import Graph, Namespace, RDF, RDFS, Literal, BNode

class rdf_writer:
    def __init__(self, namespace, spec):
        self.sh = Namespace("http://www.w3.org/ns/shacl#")
        self.xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
        self.namespace = Namespace(namespace)
        self.spec = spec

        self.shacl_graph = Graph()
        self.shacl_graph.bind("hqdm", self.namespace)
        self.shacl_graph.bind("sh", self.sh)
        self.shacl_graph.bind("xsd", self.xsd)

        self.rdf_graph = Graph()
        self.rdf_graph.bind("hqdm", self.namespace)

    def write_rdf(self, output_file_path):
        # Iterate through entities and add them to the graph
        for entity_name, entity in self.spec.entities.items():
            entity_uri = self.namespace[entity_name]
            self.rdf_graph.add((entity_uri, RDF.type, RDFS.Class))
            self.rdf_graph.add((entity_uri, RDFS.label, Literal(entity_name)))
            for supertype in entity.supertypes:
                self.rdf_graph.add((entity_uri, RDFS.subClassOf, self.namespace[supertype]))

        for relation in self.spec.base_relations:
            entity_uri = self.namespace[relation.name]
            self.rdf_graph.add((entity_uri, RDF.type, RDF.Property))
            self.rdf_graph.add((entity_uri, RDFS.label, Literal(relation.name)))
            self.rdf_graph.add((entity_uri, RDFS.domain, self.namespace[relation.entity.name]))
            self.rdf_graph.add((entity_uri, RDFS.range, self.namespace[relation.target]))

        self.rdf_graph.serialize(destination=output_file_path, format="turtle")

        print(f"RDF specification has been written to {output_file_path}")

    def write_shacl(self, output_file_path):
        for entity_name, entity in self.spec.entities.items():
            if entity.is_abstract:
                self._add_abstract_shape(entity_name)

            if entity.has_restricted_subtypes:
                self._add_restricted_subtypes_shape(entity)

            for relation in entity.relations:
                self._add_relationship_range_shape(entity_name, relation)
                if relation.has_multiplicity:
                    if relation.is_optional:
                        self._add_optional_minimum_property(entity_name, relation)
                    else:
                        self._add_relationship_minimum_cardinality(entity_name, relation)
                    if relation.multiplicity.has_maximum:
                        self._add_relationship_maximum_cardinality(entity_name, relation)
                elif not relation.is_optional:
                    self._add_relationship_minimum_cardinality(entity_name, relation, 1)
        
        self.shacl_graph.serialize(destination=output_file_path, format="turtle")

        print(f"SHACL rules have been written to {output_file_path}")
      
    def _add_abstract_shape(self, entity_name):
        shape = self.namespace[entity_name + "_abstract_shape"]
        self.shacl_graph.add((shape, self.sh.targetClass, self.namespace[entity_name]))
        self.shacl_graph.add((shape, RDF.type, self.sh.NodeShape))
        property_constraint = BNode()
        self.shacl_graph.add((shape, self.sh.property, property_constraint))
        self.shacl_graph.add((property_constraint, self.sh.path, RDF.type))
        not_constraint = BNode()
        self.shacl_graph.add((property_constraint, self.sh["not"], not_constraint))
        self.shacl_graph.add((not_constraint, self.sh.hasValue, self.namespace[entity_name]))
        self.shacl_graph.add((property_constraint, self.sh.message, 
            Literal(f"The \'{entity_name}\' entity is Abstract. No direct instances of \'{entity_name}\' are allowed, only instances of its subclasses.")))
        
    def _add_relationship_range_shape(self, entity_name, relation):
        shape = self.namespace[entity_name + "_range_for_" + relation.name + "_shape"]
        self.shacl_graph.add((shape, self.sh.targetClass, self.namespace[entity_name]))
        self.shacl_graph.add((shape, RDF.type, self.sh.NodeShape))
        property_constraint = BNode()
        self.shacl_graph.add((shape, self.sh.property, property_constraint))
        self.shacl_graph.add((property_constraint, self.sh.path, self.namespace[relation.name]))
        if relation.target != "REAL":
            self.shacl_graph.add((property_constraint, self.sh["class"], self.namespace[relation.target]))
            self.shacl_graph.add((property_constraint, self.sh.message, 
                Literal(f"The range of the \'{relation.name}\' property is limited to \'{relation.target}\' entities for entities of type \'{entity_name}\'.")))
        else:
            self.shacl_graph.add((property_constraint, self.sh.nodeKind, self.sh.Literal))
            self.shacl_graph.add((property_constraint, self.sh.datatype, self.xsd.double))
            self.shacl_graph.add((property_constraint, self.sh.message, 
                Literal(f"The range of the \'{relation.name}\' property is limited to real values for entities of type \'{entity_name}\'.")))
        
    def _add_optional_minimum_property(self, entity_name, relation):
        shape = self.namespace[entity_name + "_optional_minimum_for_" + relation.name + "_shape"]
        self.shacl_graph.add((shape, self.sh.targetClass, self.namespace[entity_name]))
        
        # Create the list for sh:or
        or_list = BNode()
        self.shacl_graph.add((shape, self.sh['or'], or_list))
        
        # First element of the list (maxCount constraint)
        max_constraint = BNode()
        self.shacl_graph.add((or_list, RDF.first, max_constraint))
        max_property = BNode()
        self.shacl_graph.add((max_constraint, self.sh.property, max_property))
        self.shacl_graph.add((max_property, self.sh.path, self.namespace[relation.name]))
        self.shacl_graph.add((max_property, self.sh.maxCount, Literal(0)))
        
        # Second element of the list (minCount constraint)
        min_list = BNode()
        self.shacl_graph.add((or_list, RDF.rest, min_list))
        min_constraint = BNode()
        self.shacl_graph.add((min_list, RDF.first, min_constraint))
        min_property = BNode()
        self.shacl_graph.add((min_constraint, self.sh.property, min_property))
        self.shacl_graph.add((min_property, self.sh.path, self.namespace[relation.name]))
        self.shacl_graph.add((min_property, self.sh.minCount, Literal(relation.multiplicity.minimum)))
        
        # Close the list
        self.shacl_graph.add((min_list, RDF.rest, RDF.nil))
        
        self.shacl_graph.add((shape, self.sh.message,
            Literal(f"If it exists, the cardinality of the '{relation.name}' property must be greater than or equal to {relation.multiplicity.minimum} for entities of type '{entity_name}'.")))
    
    def _add_relationship_minimum_cardinality(self, entity_name, relation, minimum = None):
        if minimum == None:
            minimum = relation.multiplicity.minimum
        shape = self.namespace[entity_name +  "_minimum_for_" + relation.name + "_shape"]
        self.shacl_graph.add((shape, self.sh.targetClass, self.namespace[entity_name]))
        self.shacl_graph.add((shape, RDF.type, self.sh.NodeShape))
        property_constraint = BNode()
        self.shacl_graph.add((shape, self.sh.property, property_constraint))
        self.shacl_graph.add((property_constraint, self.sh.path, self.namespace[relation.name]))
        self.shacl_graph.add((property_constraint, self.sh.minCount, Literal(minimum)))
        self.shacl_graph.add((property_constraint, self.sh.message,
            Literal(f"The cardinality of the \'{relation.name}\' property must be greater than or equal to {minimum} for entities of type \'{entity_name}\'.")))

    def _add_relationship_maximum_cardinality(self, entity_name, relation):
        shape = self.namespace[entity_name +  "_maximum_for_" + relation.name + "_shape"]
        self.shacl_graph.add((shape, self.sh.targetClass, self.namespace[entity_name]))
        self.shacl_graph.add((shape, RDF.type, self.sh.NodeShape))
        property_constraint = BNode()
        self.shacl_graph.add((shape, self.sh.property, property_constraint))
        self.shacl_graph.add((property_constraint, self.sh.path, self.namespace[relation.name]))
        self.shacl_graph.add((property_constraint, self.sh.maxCount, Literal(relation.multiplicity.maximum)))
        self.shacl_graph.add((property_constraint, self.sh.message,
            Literal(f"The cardinality of the \'{relation.name}\' property must be less than or equal to {relation.multiplicity.maximum} for entities of type \'{entity_name}\'.")))

    def _add_restricted_subtypes_shape(self, entity):
        shape = self.namespace[entity.name + "_restrict_subtypes_shape"]
        self.shacl_graph.add((shape, RDF.type, self.sh.NodeShape))
        
        self.shacl_graph.add((shape, self.sh.targetSubjectsOf, RDFS.subClassOf))

        or_constraint = BNode()
        self.shacl_graph.add((shape, self.sh['or'], or_constraint))

        # First branch of the or constraint
        first_branch = BNode()
        self.shacl_graph.add((or_constraint, RDF.first, first_branch))

        property_constraint = BNode()
        self.shacl_graph.add((first_branch, self.sh.property, property_constraint))
        path = BNode()
        self.shacl_graph.add((property_constraint, self.sh.path, path))
        self.shacl_graph.add((path, self.sh.oneOrMorePath, RDFS.subClassOf))
        self.shacl_graph.add((property_constraint, self.sh.hasValue, self.namespace[entity.name]))

        inner_or = BNode()
        self.shacl_graph.add((first_branch, self.sh['or'], inner_or))

        allowed_subclasses = entity.restricted_subtypes
        last_node = inner_or
        for subclass in allowed_subclasses:
            subclass_constraint = BNode()
            self.shacl_graph.add((last_node, RDF.first, subclass_constraint))

            prop = BNode()
            self.shacl_graph.add((subclass_constraint, self.sh.property, prop))
            path = BNode()
            self.shacl_graph.add((prop, self.sh.path, path))
            self.shacl_graph.add((path, self.sh.zeroOrMorePath, RDFS.subClassOf))
            self.shacl_graph.add((prop, self.sh.hasValue, self.namespace[subclass]))

            next_node = BNode()
            self.shacl_graph.add((last_node, RDF.rest, next_node))
            last_node = next_node

        # Add SuperClass as the last option in the inner or
        superclass_constraint = BNode()
        self.shacl_graph.add((last_node, RDF.first, superclass_constraint))
        self.shacl_graph.add((superclass_constraint, self.sh.hasValue, self.namespace[entity.name]))
        self.shacl_graph.add((last_node, RDF.rest, RDF.nil))

        # Second branch of the or constraint
        second_branch = BNode()
        rest_node = BNode()
        self.shacl_graph.add((or_constraint, RDF.rest, rest_node))
        self.shacl_graph.add((rest_node, RDF.first, second_branch))
        self.shacl_graph.add((rest_node, RDF.rest, RDF.nil))

        property_constraint = BNode()
        self.shacl_graph.add((second_branch, self.sh.property, property_constraint))
        path = BNode()
        self.shacl_graph.add((property_constraint, self.sh.path, path))
        self.shacl_graph.add((path, self.sh.oneOrMorePath, RDFS.subClassOf))
        not_constraint = BNode()
        self.shacl_graph.add((property_constraint, self.sh['not'], not_constraint))
        self.shacl_graph.add((not_constraint, self.sh.hasValue, self.namespace[entity.name]))

        # Add the message
        allowed_subclasses_string = ", ".join(allowed_subclasses)
        message = f"Subclasses of the \'{entity.name}\' entity can only inherit from the following subclasses: {allowed_subclasses_string}."
        self.shacl_graph.add((shape, self.sh.message, Literal(message)))

def get_shape_name(entity_name):
        return entity_name + "_shape"