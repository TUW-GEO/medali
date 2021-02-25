======
medali
======
.. image:: https://travis-ci.com/TUW-GEO/medali.svg?branch=master
    :target: https://travis-ci.org/TUW-GEO/medali
.. image:: https://coveralls.io/repos/github/TUW-GEO/medali/badge.svg?branch=master
    :target: https://coveralls.io/github/TUW-GEO/medali?branch=master
.. image:: https://badge.fury.io/py/medali.svg
    :target: https://badge.fury.io/py/medali
.. image:: https://readthedocs.org/projects/medali/badge/?version=latest
    :target: https://medali.readthedocs.io/en/latest/?badge=latest
.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT


*medali* stands for **ME**\ ta\ **DA**\ ta **LI**\ brary and is responsible for parsing, tagging and interpreting product metadata. 


Description
===========

*medali* should be a place to establish version-controlled metadata definitions to guarantee homogeneous reading and writing
of metadata within the scope of one product. It provides one module, the `core` module containing the class `MetaData`.
This class offers a simple interface to actual metadata items, which are defined with respect to reference metadata.
Such reference metadata can either be prepared manually as a dictionary or can be set in a configuration file.
For mature products, the configuration files are stored in the folder in "src/medali/lib" under a product ID and a metadata version.

The `Metadata` class offers the following functionality:

  * initialisation via a metadata dictionary (+ optionally a reference metadata dictionary), via a product ID and
    metadata version combination, or via a configuration file path
  * setting and encoding (from a given data type to a string) the given metadata items
  * returning and decoding (from a string to a given data type) the given metadata items
  * checking if given metadata meets the criteria defined in the reference metadata (e.g., if the value is within a list of allowed values or if the value contains a specific string, ...)

Installation
============

*medali* is a very light-weight package and has no dependencies. It can be installed via `pip`:

.. code-block:: bash

    pip install medali

Adding products
===============

A template configuration file for creating new reference metadata for a product can be found in the "templates" folder.
The file should be named according to the metadata version and should be placed in a sub-folder in "src/medali/lib" named after the product ID.
The reference metadata should have two sections:

- "Metadata": all needed tags and their data type (currently supported: string, boolean, datetime, integer, number)
- "Expected_value": should list metadata items that need to meet some specific criteria



