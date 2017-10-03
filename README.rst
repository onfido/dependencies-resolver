===============================
Dependencies Resolver
===============================

.. image:: https://img.shields.io/pypi/d/dependencies-resolver.svg
    :target: https://pypi.python.org/pypi/dependencies-resolver/
    :alt: Downloads
.. image:: https://img.shields.io/pypi/v/dependencies-resolver.svg
    :target: https://pypi.python.org/pypi/dependencies-resolver/
    :alt: Latest Version
.. image:: https://img.shields.io/pypi/l/dependencies-resolver.svg
    :target: https://pypi.python.org/pypi/dependencies-resolver/
    :alt: License

Command line tool for downloading dependencies from a configuration file.
The configuration file must follow the schema configured in `config/schema
.json`.

You can also specify the exact path to the file if that was uploaded manually and not by the `s3-uploader`.

This is part of Onfido's team blobs store project.

The purpose of this tool is to download the project's dependencies
configured from a configuration file. Resources can be uploaded using the
complimentary tool the `s3-uploader`.


Installing
==========

.. code-block:: shell

	$ pip install dependencies-resolver


How to use
==========
Example for using the tool

.. code-block:: shell

	dependencies-resolver -c dependencies.json


Get the project
===============

	1. Clone the git repository

	.. code-block:: shell

		$ git clone https://github.com/onfido/dependencies-resolver

	2. Install a virtualenv

	.. code-block:: shell

		$ sudo apt-get install python-virtualenv

	3. Create a new virtualenv

	.. code-block:: shell

		$ virtualenv dependencies_resolver_ve

	4. Install project's requirements

	.. code-block:: shell

		$ dependencies_resolver_ve/bin/pip install -r requirements.txt



Reporting Issues
================
If you have suggestions, bugs or other issues specific to this library, open
an issue, or just be awesome and make a pull request out of it.

