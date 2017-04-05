from __future__ import print_function
from __future__ import division

from setuptools import setup, find_packages
from pip.req import parse_requirements

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    _license = f.read()

install_requirements = parse_requirements('requirements.txt', session=False)
requirements = [str(ir.req) for ir in install_requirements]

setup(
    name='dependencies-resolver',
    version='0.0.5',
    description='Command line tool for downloading dependencies from config '
                'file',
    long_description=readme,
    author='Onfido',
    url='https://github.com/onfido/dependencies-resolver/',
    license=_license,
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'dependencies-resolver = dependencies_resolver.main:main', ], },
    keywords=['python', 's3', 'aws', 'download', 'binaries', 'resources',
              'boto3', 'dependencies', 'downloader', 'dependency-management'],
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
