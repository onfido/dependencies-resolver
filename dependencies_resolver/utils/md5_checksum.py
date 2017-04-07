import binascii
import hashlib
import math
import os

from dependencies_resolver.config.configuration import DEFAULT_CHUNK_SIZE


def _get_part_size(file_path, multipart_upload):
    """This function gets a file path and a regular expression object
    contains the number of parts the remote copy of the file is composed
    of, and return the part size used to upload each part represented as
    the next power of 2.

    Examples:
        1. An example of a MD5 hash of multi-part uploaded file:
            d41d8cd98f00b204e9800998ecf8427e-2

            Explanation:
            d41d8cd98f00b204e9800998ecf8427e - The concatenation of all the
            MD5 hashes of all the parts
            2 - The number of parts for this file.

            In that case, the regex result will be:
            -2 - A delimiter concatenated to the total number of parts for this
            file.

        2. An example of a MD5 hash of single-part file:
            341ffd9e59f9271ad9507e646dfff6f9

            In that case, the regex result will be None

    :param file_path: The path to the local file, for getting the file size
    :param multipart_upload: A regular expression object to indicate
    whether the remote copy of the file was uploaded as multi-part file. If
    not, the object will be None.
    :return: The part size of the file based on the size and number of parts.
    """
    file_size = float(os.path.getsize(file_path))
    num_of_parts = float(str(multipart_upload.group(0)).replace('-', ''))
    next_power_of_2 = 0
    if num_of_parts > 0:
        # This is needed because that's how boto3's S3 upload function works.
        # If the file is above some threshold, it splits it into parts
        # and upload the parts separately and then S3 combining everything
        # together remotely. To calculate each part size, you need to get the
        # total file size divided by the number of parts, and convert that
        # result into MB and round it to the next power of two.
        size_in_mb = math.ceil(file_size / num_of_parts / 1024 / 1024)
        size_in_bytes = int(size_in_mb * 1024 * 1024)
        next_power_of_2 = math.pow(2, math.ceil(math.log(
            size_in_bytes)/math.log(2)))
    return int(next_power_of_2)


def get_aws_like_md5_checksum(file_path, multipart_regex):
    """This function gets a file path and returns the appropriate MD5
    checksum for the file.
    If the remote copy of the file stored in S3 uploaded using multipart
    upload operation then a different algorithm to calculate the file's MD5
    checksum is applied.

    The algorithm for calculating the MD5 checksum for multipart uploaded
    file (Based on AWS documentation):
    The official documentation about how complete multipart upload is done:
    http://docs.aws.amazon.com/AmazonS3/latest/API/mpUploadComplete.html
    A StackOverflow thread which stems from the link above on how to
    calculate the complete md5 hash:
    http://stackoverflow.com/a/19896823/2455626


    1. Calculate the MD5 hash for each uploaded part of the file.
    2. Concatenate the hashes into a single binary string.
    3. Calculate the MD5 hash of that result.
    4. Concatenate the resulted MD5 hash with a dash
       and number of file parts.

    Examples:
    1. A MD5 hash of single-part uploaded file: d41d8cd98f00b204e9800998ecf8427e
    2. A MD5 hash of multi-part uploaded file:
        d41d8cd98f00b204e9800998ecf8427e-2

        Explanation:
        d41d8cd98f00b204e9800998ecf8427e - The concatenation of all the
        MD5 hashes of all the part
        2 - The number of parts for this file.

    :param file_path: The path to the local file.
    :param multipart_regex: A regular expression result object to indicate
    whether the remote copy of the file uploaded using multipart upload
    :return: The MD5 checksum for the file.
    """

    md5_hash = hashlib.md5()
    if multipart_regex:
        part_size = _get_part_size(file_path, multipart_regex)
        block_count = 0
        md5string = ""
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(part_size), ""):
                md5_hash = hashlib.md5()
                md5_hash.update(block)
                md5string = md5string + binascii.unhexlify(
                    md5_hash.hexdigest())
                block_count += 1
        md5_hash = hashlib.md5()
        md5_hash.update(md5string)
        return md5_hash.hexdigest() + "-" + str(block_count)
    else:
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(DEFAULT_CHUNK_SIZE), ""):
                md5_hash.update(block)
        return md5_hash.hexdigest()
