from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re

import boto3
from botocore.exceptions import ClientError

from dependencies_resolver.utils.exception_handler import handle_exception

# Credentials are being read from shared credentials file configured for
# the AWS command line. Usually this configured as: ~/.aws/credentials

# More details at:
# http://boto3.readthedocs.io/en/latest/guide/configuration.html#shared-credentials-file
s3_client = boto3.client('s3')


def get_latest_version(bucket, name):
    """This function gets a bucket and a name of resource, and returns the 
    latest version stored for this resource.
    
    :param bucket: The name of the bucket.
    :param name: The name of the resource.
    :return: The latest version for this resource stored in the bucket.
    """
    keys_list = []
    bucket_keys = s3_client.list_objects(Bucket=bucket, Prefix=name)

    for key in bucket_keys['Contents']:
        keys_list.append(key['Key'])
    most_recent_key = sorted(keys_list, reverse=True)[0]

    # The key is in the format of: BINARY-NAME/YYYY-mm-dd-HH-mm-ss/BINARY-FILE
    # and we want only the date (which refers as the version) to be extracted
    # hence the regex
    extracted_version = re.search(r'/([^/]+)/', most_recent_key).group(1)
    return extracted_version


def version_exists(bucket, name, version):
    """This function gets a bucket, resource name and version and checks if 
    the version exists for that resource. Returns True if exists, 
    and False otherwise.
    
    :param bucket: The name of the bucket.
    :param name: The name of the resource.
    :param version: The version of the resource.
    :return: Returns True if this version exists, False otherwise.
    """
    if version == 'latest':
        version = get_latest_version(bucket, name)
    return object_exists(bucket, name + '/' + version), version


def get_key(bucket, name, version):
    """This function gets a bucket name, resource name and version and 
    returns the constructed key if the version exists for that resource, 
    or ValueError exception is being raised otherwise.
    
    :param bucket: The name of the bucket.
    :param name: The name of the resource.
    :param version: The version of the resource.
    :return: The S3 key for downloading the resource if the version exists, 
    ValueError exception is being raised otherwise.
    """
    binary_version_exists, version = version_exists(bucket, name, version)

    if not binary_version_exists:
        raise ValueError(
            'Version ({0}) not found for this binary'.format(version))

    return name + '/' + version + '/' + name


def object_exists(bucket, prefix):
    """This function gets a bucket name and a prefix 
    and returns True if the path exists and contains any content in it,
    or False otherwise.
    
    :param bucket: The name of the bucket.
    :param prefix: The prefix to search inside the bucket.
    :return: True if the path exists and contains anything, and False 
    otherwise.
    """
    response = s3_client.list_objects(Bucket=bucket, Prefix=prefix)
    return True if 'Contents' in response else False


def download(bucket, name, version, location):
    """This function is a wrapper function for boto3's S3 download function 
    which gets a bucket name, a resource name, a version and a location to 
    download to, and downloading the resource if it exists and has the 
    specified version as well. Any failure will cause the exception to be 
    printed to stdout, and the program to exit.
    
    :param bucket: The name of the bucket.
    :param name: The name of the resource.
    :param version: The version of the resource.
    :param location: The location in which the resource would be downloaded to.
    :return: Nothing, unless an exception is being raised.
    """
    try:
        if not object_exists(bucket, name):
            raise ValueError(
                'Binary ({0}) not found in the repository'.format(name))

        try:
            if not os.path.exists(location):
                os.makedirs(location)
        except OSError:
            handle_exception(
                'Directory could not be created. Check permissions '
                'to ({0})'.format(location))

        download_path = location + name
        try:
            key = get_key(bucket, name, version)
            with open(download_path, 'wb') as obj:
                s3_client.download_fileobj(bucket, key, obj)
        except IOError:
            handle_exception(
                'File could not be saved. Check permissions to ({0})'.format(
                    location))
        except ClientError as ex:
            handle_exception(ex.message)
    except ValueError as ex:
        handle_exception(ex.message)
