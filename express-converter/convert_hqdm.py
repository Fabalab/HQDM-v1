import os
from express_classes import *
from rdf_writer import rdf_writer

# File paths
express_file_path = os.path.join(os.path.dirname(__file__), "..\\hqdm-express.txt")
rdf_file_path = os.path.join(os.path.dirname(__file__), "..\\hqdm-rdf.ttl")
shacl_file_path = os.path.join(os.path.dirname(__file__), "..\\hqdm-shacl.ttl")

hqdmUri = "http://example.org/hqdm#"

# Read the EXPRESS file
with open(express_file_path, 'r') as file:
    txt = file.read()

# Parse the EXPRESS specification
spec = Spec(txt)

# Define namespaces
writer = rdf_writer(hqdmUri, spec)
writer.write_rdf(rdf_file_path)
writer.write_shacl(shacl_file_path)

