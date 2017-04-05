from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import pytest
from dependencies_resolver.dependency_handler.validation import validate_data
from jsonschema import ValidationError

mocked_dependencies = {
    "repository": "onfido-blobs",
    "dependencies": [
        {
            "name": "model.pb",
            "version": "latest",
            "location": "/tmp/model"
        }
    ]
}


def test_bad_repository_url():
    """A test to check if the repository is a valid S3 bucket name.
    A valid S3 bucket name should contain 's3://' as the prefix, to make it 
    explicit that the remote repository is S3 bucket.
    
    :return: Nothing, an exception is being raised. 
    """
    with pytest.raises(ValidationError):
        validate_data(mocked_dependencies)


def test_location_without_trailing_slash():
    """A test to check if the location property of the dependency is ending 
    with a trailing slash, as it should ALWAYS be a directory.
    
    :return: Nothing, an exception is being raised.
    """
    mocked_dependencies['repository'] = 's3://' + mocked_dependencies[
                                                      'repository'][5:]
    with pytest.raises(ValidationError):
        validate_data(mocked_dependencies)
