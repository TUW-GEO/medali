# Copyright (c) 2021, TU Wien, Department of Geodesy and Geoinformation
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of TU Wien, Department of Geodesy and Geoinformation
#      nor the names of its contributors may be used to endorse or promote
#      products derived from this software without specific prior written
#      permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL TU WIEN DEPARTMENT OF GEODESY AND
# GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
Parsing and modification of the metadata.

"""

import re
import os
import numbers
import datetime
from dateutil.parser import parse
from pprint import pformat
from configparser import ConfigParser


class MetaData:
    """ Metadata base class to store metadata, set and get metadata. """
    def __init__(self, metadata, ref_metadata=None):
        """
        Creates a `MetaData` instance from a given metadata dictionary
        and a dictionary storing information about expected metadata
        attributes, metadata value data types, and expected metadata values.

        Parameters
        ----------
        metadata : dict
            Dictionary containing metadata attributes and decoded values.
        ref_metadata : dict
            Dictionary containing expected metadata attributes plus data types
            under the key "Metadata", and expected metadata values under the key
            "Expected_value".

        """
        self._meta = {}
        self._ref_meta = {} if ref_metadata is None else ref_metadata
        self._set_input_metadata(metadata)

    @classmethod
    def from_cfg_file(cls, metadata, cfg_filepath):
        """
        Creates a `MetaData` instance from a given metadata dictionary and
        a config file.

        Parameters
        ----------
        metadata : dict
            Dictionary containing metadata attributes and decoded values.
        cfg_filepath : str
            Path to metadata config file.

        Returns
        -------
        MetaData

        """
        if not os.path.exists(cfg_filepath):
            err_msg = "'{}' does not exist.".format(cfg_filepath)
            raise IOError(err_msg)
        ref_metadata = read_config(cfg_filepath)

        return cls(metadata, ref_metadata)

    @classmethod
    def from_product_version(cls, metadata, prod_name, version_id):
        """
        Creates a `MetaData` instance from a given metadata dictionary,
        a product name and a version ID.

        Parameters
        ----------
        metadata : dict
            Dictionary containing metadata attributes and decoded values.
        prod_name : str
            Name of the product, e.g. "SIG0".
        version_id : str
            Metadata version.

        Returns
        -------
        MetaData

        """
        root_dirpath = os.path.dirname(os.path.abspath(__file__))
        cfg_filepath = os.path.join(root_dirpath, "lib", prod_name.lower(), version_id + '.ini')

        return cls.from_file(metadata, cfg_filepath)

    def to_pretty_frmt(self):
        """ str : Returns metadata dictionary in a formatted string. """
        return pformat(self._meta, indent=4)

    def _set_input_metadata(self, metadata):
        """
        Sets metadata attributes and values according to the given metadata dictionary.
        If a required attribute is not given it is set to 'null'.

        Parameters
        ----------
        metadata : dict
            Dictionary containing metadata attributes and decoded values.

        """
        for key, value in metadata.items():
            self._set_metadata(key, value)

        for key, value in self._ref_meta['Metadata'].items():
            if key not in self._meta:
                self._meta[key] = 'null'

    def _set_metadata(self, key, value):
        """
        Encodes the given metadata value according to the given metadata attribute and
        stores it/overwrites it.

        Parameters
        ----------
        key : str
            Metadata attribute.
        value : any
            Metadata value.

        """
        if self._ref_meta:
            if key in self._ref_meta['Metadata'].keys():
                if self._ref_meta['Metadata'][key] == 'string':
                    if isinstance(value, str):
                        self._meta[key] = value
                    else:
                        err_msg = "Metadata information for key '{}' has to be string.".format(key)
                        raise ValueError(err_msg)
                elif self._ref_meta['Metadata'][key] == 'boolean':
                    if isinstance(value, bool):
                        self._meta[key] = str(value)
                    else:
                        err_msg = "Metadata information for key '{}' has to be boolean.".format(key)
                        raise ValueError(err_msg)
                elif self._ref_meta['Metadata'][key] == 'integer':
                    if isinstance(value, int):
                        self._meta[key] = str(value)
                    else:
                        err_msg = "Metadata information for key '{}' has to be integer".format(key)
                        raise ValueError(err_msg)
                elif self._ref_meta['Metadata'][key] == 'number':
                    if isinstance(value, numbers.Number):
                        self._meta[key] = str(value)
                    else:
                        err_msg = "Metadata information for key '{}' has to be number".format(key)
                        raise ValueError(err_msg)
                elif self._ref_meta['Metadata'][key] == 'datetime':
                    if isinstance(value, datetime.datetime):
                        self._meta[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        err_msg = "Metadata information for key '{}' has to be datetime object".format(key)
                        raise ValueError(err_msg)
                else:
                    self._meta[key] = str(value)
            else:
                err_msg = "Metadata attribute '{}' is not given in the product reference.".format(key)
                raise KeyError(err_msg)
        else:
            self._meta[key] = str(value)

    def _get_metadata(self, attribute):
        """
        Decodes and returns metadata value according to the given attribute.

        Parameters
        ----------
        attribute : str
            Metadata attribute.

        Returns
        -------
        value : any
            Decoded metadata value.

        """
        if attribute not in self._meta.keys():
            err_msg = "Metadata attribute '{}' can not be found.".format(attribute)
            raise KeyError(err_msg)

        if self._ref_meta:
            if self._meta[attribute] == 'null':
                value = None
            elif self._ref_meta['Metadata'][attribute] == 'boolean':
                value = self._meta[attribute] == 'True'
            elif self._ref_meta['Metadata'][attribute] == 'integer':
                value = int(self._meta[attribute])
            elif self._ref_meta['Metadata'][attribute] == 'number':
                value = float(self._meta[attribute])
            elif self._ref_meta['Metadata'][attribute] == 'datetime':
                value = datetime.datetime.strptime(self._meta[attribute], "%Y-%m-%d %H:%M:%S")
            else:
                value = self._meta[attribute]
        else:
            value = self._meta[attribute]

        return value

    def check_metadata(self, metadata):
        """
        Checks if a given metadata dictionary is in compliance with the
        corresponding reference metadata.

        Parameters
        ----------
        metadata : dict
            Metadata items with their values encoded as strings.

        Returns
        ----------
        missing_keys : list
            Metadata keys that are missing with respect to the
            reference metadata.
        suspicious_keys : list
            Metadata keys that have suspicious values
            when compared to rules defined in the reference metadata.
        empty_keys : list
            Metadata keys that contain a 'null' value.

        """

        exp_ref_meta = self._ref_meta['Expected_value']

        missing_keys = []
        suspicious_keys = []
        empty_keys = []
        for key in exp_ref_meta:
            if key not in metadata.keys():
                missing_keys.append(key)
            elif metadata[key] == 'null':
                empty_keys.append(key)
            elif isinstance(exp_ref_meta[key], list):
                if metadata[key] not in exp_ref_meta[key]:
                    suspicious_keys.append(key)
            elif exp_ref_meta[key] in ('integer', 'number'):
                if not metadata[key].replace('.','',1).isnumeric():
                    suspicious_keys.append(key)
            elif exp_ref_meta[key] == 'boolean':
                if metadata[key] not in ['False', 'True']:
                    suspicious_keys.append(key)
            elif exp_ref_meta[key] == 'datetime':
                if not isdate(metadata[key]):
                    suspicious_keys.append(key)
            elif exp_ref_meta[key].startswith('pattern'):
                value = exp_ref_meta[key].replace(', ', ',')
                value = value.split(',')
                pattern = value[1]
                if not re.search(pattern, metadata[key]):
                    suspicious_keys.append(key)
            elif exp_ref_meta[key] == 'string':
                dummy = 1
            else:
                print(key)

        return missing_keys, suspicious_keys, empty_keys

    def __str__(self):
        """ str : String representation of metadata object. """
        return self.to_pretty_frmt()

    def __setitem__(self, key, value):
        """
        Sets a metadata attribute.

        Parameters
        ----------
        key : str
            Metadata attribute.
        value : any
            Metadata value.

        """
        self._set_metadata(key, value)

    def __getitem__(self, item):
        """
        Returns metadata value according to the given metadata item.

        Parameters
        ----------
        item : str
            Metadata attribute.

        Returns
        -------
        any
            Metadata value.

        """
        return self._get_metadata(item)


def read_config(filepath):
    """
    Parse a metadata config file.

    Parameters
    ----------
    filepath : str
        Path to the metadata config file.

    Returns
    -------
    ds : dict
        Parsed metadata config file as a dictionary.

    """
    config = ConfigParser()
    config.optionxform = str
    config.read(filepath)

    ds = {}

    for section in config.sections():

        ds[section] = {}
        for item, value in config.items(section):

            if value.startswith('list'):
                value = value.replace(', ', ',')
                value = value.split(',')
                value.pop(0)

            ds[section][item] = value

    return ds


def isdate(string):
    """
    Checks if a given string can be translated into a date representation.

    Parameters
    ----------
    string : str
        Datetime string.

    Returns
    -------
    bool
        True if `string` is a date, else false.

    """
    try:
        parse(string)
        return True
    except ValueError:
        return False

