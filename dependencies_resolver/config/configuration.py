import os

SCHEMA_FILE_LOCATION = os.path.join(os.path.dirname(__file__), 'schema.json')
REGEX_MULTIPART_UPLOAD_PATTERN = r'-\d+'
DEFAULT_CHUNK_SIZE = 4096
