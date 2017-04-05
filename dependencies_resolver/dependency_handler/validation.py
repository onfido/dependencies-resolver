from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from jsonschema import ValidationError
from jsonschema import validate

from dependencies_resolver.config.configuration import SCHEMA_FILE_LOCATION
from dependencies_resolver.schema.loader import load_schema


def validate_data(data):
    """This function validates the data from the configuration file provided.
    If the validation breaks, a ValidationError exception is being raised.
    
    :param data: The JSON configuration file as dictionary object.
    :return: Nothing, unless there's an error and then a ValidationError 
    exception is being raised.
    """
    if data['repository'][0:5] != 's3://':
        raise ValidationError('Not a valid S3 url')

    for dependency in data['dependencies']:
        if not str(dependency['location']).endswith('/'):
            raise ValidationError('Location does not end with trailing slash')


def validate_schema(data):
    """This function gets a data from the configuration file provided, 
    and checks whether the data is followed by the pre-defined schema.
    If the validation breaks, a ValueError exception is being raised.
    
    :param data: The JSON configuration file as dictionary object.
    :return: Nothing, unless there's an error and then a ValidationError 
    exception is being raised.
    """
    schema = load_schema(SCHEMA_FILE_LOCATION)
    validate(data, schema)
