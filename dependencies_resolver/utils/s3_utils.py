from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re

import boto3
import botocore
from botocore.exceptions import ClientError

from dependencies_resolver.config.configuration import \
    REGEX_MULTIPART_UPLOAD_PATTERN
from dependencies_resolver.utils import md5_checksum
from dependencies_resolver.utils.exception_handler import handle_exception

# Credentials are being read from shared credentials file configured for
# the AWS command line. Usually this configured as: ~/.aws/credentials

# More details at:
# http://boto3.readthedocs.io/en/latest/guide/configuration.html#shared-credentials-file
s3_client = boto3.client('s3')


def get_object_md5_checksum(bucket, key):
    """This function returns the MD5 checksum for the remote file.
    If the file was uploaded as a single-part file, the MD5 checksum will be
    the checksum of the file content.
    However, if the file was uploaded as multi-part file,
    AWS is calculating the MD5 the following way (Based on AWS documentation):
        1. Calculate the MD5 md5_hash for each uploaded part of the file.
        2. Concatenate the hashes into a single binary string.
        3. Calculate the MD5 md5_hash of that result.
        4. Concatenate the resulted MD5 md5_hash with a dash
           and number of file parts.

    :param bucket: The name of the bucket.
    :param key: The full path to the remote file.
    :return: The MD5 checksum for the remote file.
    """
    try:
        md5_checksum = s3_client.head_object(
            Bucket=bucket,
            Key=key
        )['ETag'][1:-1]
    except botocore.exceptions.ClientError:
        md5_checksum = ''
    return md5_checksum


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
    _version_exists, version = version_exists(bucket, name, version)

    if not _version_exists:
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


def file_already_exists(bucket, key, download_path):
    """This function checks if there's already a local copy of the remote
    file to be downloaded, and if so checks whether the local copy of the
    remote file is identical (same MD5 checksum) to the remote file.

    The MD5 hash check flow:
    We check the MD5 checksum for the remote copy of that file.
    The problem in the result of that checksum is that AWS has a unique
    way of generating a checksum to a file on S3 that was uploaded using
    multi-part operation.

    What multi-part operation you're asking? Well, when a file is being
    uploaded to S3 and is above some threshold, boto3's S3 upload library is
    automatically breaking the file into parts and upload each part separately
    to make the upload process easier. In that way, the file is then stored
    in S3 as single-part file but actually composed of all the parts together.

    Now, when asking the MD5 checksum of the file, if the file uploaded as a
    single-part, that checksum will be traditional MD5 hash as we expect.
    But, if the file was uploaded as multi-parts file, then AWS has a
    different algorithm for calculating the checksum of the file:

    1. Calculate the MD5 hash for each uploaded part of the file.
    2. Concatenate (hex concatenation) the hashes into a single binary string.
    3. Calculate the MD5 hash of that result.
    4. Concatenate the resulted MD5 hash with a dash and number of file parts.

    So an example for that MD5 hash could be something like:
    d41d8cd98f00b204e9800998ecf8427e-2
    Which mean the file in S3 is composed of 2 files.
    In order to get that exact md5 hash for the local file to check the
    identity of both files, we need to break the local file into the same number
    of parts and make sure we have the same size for each part, and that's
    been done in the code as well. Then, we can check for the md5 hashes and
    determine whether the files are identical or not.


    :param bucket: The name of the bucket.
    :param key: The key to the remote file.
    :param download_path: The path to the local copy of the remote file.
    :return: True if the remote and local files are identical, and False
    otherwise.
    """
    identical_files = False
    if os.path.isfile(download_path):
        remote_file_checksum = get_object_md5_checksum(bucket, key)
        multipart_regex = re.search(REGEX_MULTIPART_UPLOAD_PATTERN,
                                    remote_file_checksum)
        local_file_checksum = md5_checksum.get_aws_like_md5_checksum(
            download_path,
            multipart_regex)
        identical_files = remote_file_checksum == local_file_checksum
    return identical_files


def download(bucket, name, version, location):
    """This function is a wrapper function for boto3's S3 download function 
    which gets a bucket name, a resource name, a version and a location to 
    download to.

    The function first checks if the specified resource exists locally and
    has the same checksum as the remote file.

    If so, the resource won't be downloaded as it already
    in its the latest version.

    Otherwise, the resource will be downloaded if it exists remotely with
    the specified version.

    Any failure will cause the exception to be printed to stdout, and the
    program to exit.
    
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
            if not file_already_exists(bucket, key, download_path):
                print('Downloading: [resource: {0}], [version: {1}]'.format(
                    name, version))
                with open(download_path, 'wb') as obj:
                    s3_client.download_fileobj(bucket, key, obj)
            else:
                print('Skipping: [resource: {0}], [status: local copy is '
                      'up to date!]'.format(name))
        except IOError:
            handle_exception(
                'File could not be saved. Check permissions to ({0})'.format(
                    location))
        except ClientError as ex:
            handle_exception(ex.message)
    except ValueError as ex:
        handle_exception(ex.message)
