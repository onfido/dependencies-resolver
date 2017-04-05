from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

import pytest
from dateutil.tz import tzutc
from mock import patch

from dependencies_resolver.utils.s3_utils import get_latest_version, get_key


def _mock_get_response(self, operation_name, kwarg):
    """This function mocks the response for the S3 boto client for testing 
    purposes. 
    
    :param self: The original instance of the client, is not being used but 
    is part of the function signature.
    :param operation_name: The name of the operation to the client.
    :param kwarg: Additional arguments.
    :return: The mocked response.
    """
    if operation_name == 'ListObjects':
        # Returns a mocked response
        response = {'Name': kwarg['Bucket'], 'ResponseMetadata': {
            'HTTPStatusCode':
                200,
            'RetryAttempts': 0},
                    'MaxKeys': 1000, 'Prefix': kwarg['Prefix'], 'Marker': '',
                    'EncodingType': 'url', 'IsTruncated': False,
                    'Contents': [{'LastModified': datetime.datetime(2017, 3,
                                                                    22, 18,
                                                                    50, 32,
                                                                    tzinfo=tzutc()),
                                  'StorageClass': 'STANDARD',
                                  'Key': 'model/2011-01-01-23-44-12/model',
                                  'Size': 418}]}
        return response


def _mock_get_empty_response(self, operation_name, kwarg):
    """This function gets the mocked response for the S3 boto client, 
    but delete the content so it is a empty mocked response.
    
    :param self: The original instance of the client, is not being used but 
    is part of the function signature.
    :param operation_name: The name of the operation to the client.
    :param kwarg: kwarg: Additional arguments.
    :return: The empty mocked response.
    """
    response = _mock_get_response(self, operation_name, kwarg)
    del response['Contents']
    return response


def test_get_latest_version():
    """A test to check that the latest version stored remotely is indeed 
    being retrieved.
    
    :return: True, unless the function is not working as we expected.
    """
    with patch('botocore.client.BaseClient._make_api_call',
               new=_mock_get_response):
        version = get_latest_version('test-bucket', 'model')
        expected_version = '2011-01-01-23-44-12'
        assert version == expected_version


def test_get_key_non_existent():
    """A test to check that if the version does not exists,
    a ValueError exception will be raised.
    
    :return: Nothing, an exception is being raised.
    """
    with pytest.raises(ValueError):
        with patch('botocore.client.BaseClient._make_api_call',
                   new=_mock_get_empty_response):
            get_key('test-bucket', 'model', '2004-05-02-12-34-55')


def test_get_key():
    """A test to check that if the version does exists remotely, 
    the correct key will be composed.
    
    :return: True, unless the function is not working as we expected.
    """
    with patch('botocore.client.BaseClient._make_api_call',
               new=_mock_get_response):
        key = get_key('test-bucket', 'model', '2011-01-01-23-44-12')
        expected_key = 'model/2011-01-01-23-44-12/model'
        assert key == expected_key
