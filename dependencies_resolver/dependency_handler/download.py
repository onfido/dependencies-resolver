from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from dependencies_resolver.utils import s3_utils


def download_dependencies(dependencies_data):
    """This function gets a list of dependencies and a remote repository.
    The dependencies are being downloaded to the specified location per 
    dependency.
    
    :param dependencies_data: A JSON which contains a repository and a list 
    of dependencies to be downloaded. 
    :return: Nothing, unless an Exception is being raised.
    """
    # Removing the s3:// prefix from the repository name
    base_repository = dependencies_data['repository'][5:]
    dependencies = dependencies_data['dependencies']

    for dependency in dependencies:
        name = dependency['name']
        version = dependency['version']
        location = dependency['location']
        s3_utils.download(bucket=base_repository, name=name,
                          version=version, location=location)
