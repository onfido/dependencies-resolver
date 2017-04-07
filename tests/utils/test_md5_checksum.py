import re
import tempfile

from dependencies_resolver.config.configuration import \
    REGEX_MULTIPART_UPLOAD_PATTERN
from dependencies_resolver.utils.md5_checksum import get_aws_like_md5_checksum
from tests.utils.test_s3_utils import MOCKED_MD5_CHECKSUM


def test_get_md5_checksum_no_multipart_upload():
    """A test to check we get the desired md5 checksum for a file that has
    not uploaded using multipart upload.

    :return: True, unless the function is not working as we expected.
    """
    with tempfile.NamedTemporaryFile() as f:
        md5_checksum = get_aws_like_md5_checksum(f.name, None)
        assert md5_checksum == MOCKED_MD5_CHECKSUM[1:-1].split('-')[0]


def test_get_md5_checksum_multipart_upload():
    """A test to check we get the desired md5 checksum for a file that has
    uploaded using multipart upload.

    :return: True, unless the function is not working as we expected.
    """
    with tempfile.NamedTemporaryFile() as f:
        multipart_regex_result = re.search(REGEX_MULTIPART_UPLOAD_PATTERN,
                                           MOCKED_MD5_CHECKSUM)
        md5_checksum = get_aws_like_md5_checksum(f.name, multipart_regex_result)
        assert md5_checksum == MOCKED_MD5_CHECKSUM[1:-1]
