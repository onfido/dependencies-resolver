from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import json
import sys

from jsonschema import ValidationError

from dependencies_resolver.dependency_handler.download import \
    download_dependencies
from dependencies_resolver.dependency_handler.validation import \
    validate_schema, \
    validate_data
from dependencies_resolver.utils.exception_handler import handle_exception


def resolve_dependencies(args):
    """Main function to handle the dependencies from the config file.
    The dependencies will be downloaded from the specified S3 repository
    and will be placed in the location provided for the specific
    dependency from the configuration file.

    :param args: The user's arguments supplied from the main function.
    """
    try:
        config_file = args.config
        with open(config_file, 'r') as json_file:
            dependencies_data = json.load(json_file)
        validate_schema(dependencies_data)
        validate_data(dependencies_data)
        download_dependencies(dependencies_data)
        sys.exit()
    except IOError:
        handle_exception('File could not be opened')
    except ValueError:
        handle_exception('File could not be parsed')
    except ValidationError:
        handle_exception('File could not be validated')
    except Exception:
        handle_exception('Unknown error occurred')
