from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import json


def load_schema(schema_file_location):
    """This function gets a path to a JSON schema, opens and loads it as a 
    dictionary object, and then returns it.
    
    :param schema_file_location: The path to the schema JSON file.
    :return: The loaded schema as dictionary object.
    """
    with open(schema_file_location) as f:
        schema = json.load(f)
        return schema
