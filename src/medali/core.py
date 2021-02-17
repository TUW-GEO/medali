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
        self._ref_meta = {'Metadata': dict(), 'Expected_value': dict()} if ref_metadata is None else ref_metadata
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

        return cls.from_cfg_file(metadata, cfg_filepath)

    def to_pretty_frmt(self):
        """ str : Returns metadata dictionary in a formatted string. """
        return pformat(self._meta, indent=4)

    def to_tags(self):
        """ dict : Returns metadata as a dictionary containing encoded values. """
        return self._meta

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

    def _set_metadata(self, attr, value):
        """
        Encodes the given metadata value according to the given metadata attribute and
        stores it/overwrites it.

        Parameters
        ----------
        attr : str
            Metadata attribute.
        value : any
            Metadata value.

        """
        # convert back and forth to execute expected value test with decoded values
        enc_value = self._encode(attr, value)
        dec_value = self._decode(attr, enc_value)
        if not self._is_expected(attr, dec_value):
            expected_values = self._ref_meta['Expected_value'].get(attr)
            err_msg = "Metadata value '{}' is not in compliance with '{}'".format(value, expected_values)
            raise ValueError(err_msg)

        self._meta[attr] = self._encode(attr, value)

    def _get_metadata(self, attr):
        """
        Decodes and returns metadata value according to the given attribute.

        Parameters
        ----------
        attr : str
            Metadata attribute.

        Returns
        -------
        value : any
            Decoded metadata value.

        """
        if attr not in self._meta.keys():
            err_msg = "Metadata attribute '{}' can not be found.".format(attr)
            raise KeyError(err_msg)

        return self._decode(attr, self._meta[attr])

    def _is_expected(self, attr, value):
        """
        Checks if a given metadata value is in compliance with the
        corresponding expected values in the reference metadata.

        Parameters
        ----------
        attr : str
            Metadata attribute.
        value : any
            Decoded metadata value.

        Returns
        ----------
        is_expected : bool
            True if the given metadata value is expected, else false.

        """
        exp_values = self._ref_meta['Expected_value'].get(attr)
        is_expected = True
        if exp_values and (value not in [None, 'null']):
            if isinstance(exp_values, list):
                if value not in exp_values:
                    is_expected = False
            elif exp_values.startswith('pattern'):
                exp_value = exp_values.replace(', ', ',')
                pattern = exp_value.split(',')[1]
                if not re.search(pattern, value):
                    is_expected = False

        return is_expected

    def _decode(self, attr, value):
        """
        Decodes value according to the given attribute.

        Parameters
        ----------
        attr : str
            Metadata attribute.
        value : str
            Metadata value.

        Returns
        -------
        dec_value : any
            Decoded metadata value.

        """
        if self._ref_meta['Metadata']:
            if attr in self._ref_meta['Metadata'].keys():
                if value == 'none':
                    dec_value = None
                elif self._ref_meta['Metadata'][attr] == 'boolean':
                    dec_value = value == 'True'
                elif self._ref_meta['Metadata'][attr] == 'integer':
                    dec_value = int(value)
                elif self._ref_meta['Metadata'][attr] == 'number':
                    dec_value = float(value)
                elif self._ref_meta['Metadata'][attr] == 'datetime':
                    dec_value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                else:
                    dec_value = value
            else:
                err_msg = "Attribute '{}' is not given in the reference metadata."
                raise KeyError(err_msg)
        else:
            dec_value = value

        return dec_value

    def _encode(self, attr, value):
        """
        Encodes value according to the given attribute.

        Parameters
        ----------
        attr : str
            Metadata attribute.
        value : any
            Metadata value.

        Returns
        -------
        enc_value : str
            Encoded metadata value.

        """
        err_msg_frmt = "Metadata value for attribute '{}' has to be '{}'."
        if self._ref_meta['Metadata']:
            if attr in self._ref_meta['Metadata'].keys():
                dtype = self._ref_meta['Metadata'][attr]
                if value is None:
                    enc_value = 'none'
                elif isinstance(value, str):  # nothing to encode, but check if the value is convertable
                    try:
                        self._decode(attr, value)
                    except Exception:
                        raise ValueError(err_msg_frmt.format(attr, dtype))
                    enc_value = value
                elif dtype == 'boolean':
                    if isinstance(value, bool):
                        enc_value = str(value)
                    else:
                        raise ValueError(err_msg_frmt.format(attr, dtype))
                elif dtype == 'integer':
                    if isinstance(value, int):
                        enc_value = str(value)
                    else:
                        raise ValueError(err_msg_frmt.format(attr, dtype))
                elif dtype == 'number':
                    if isinstance(value, numbers.Number):
                        enc_value = str(value)
                    else:
                        raise ValueError(err_msg_frmt.format(attr, dtype))
                elif dtype == 'datetime':
                    if isinstance(value, datetime.datetime):
                        enc_value = value.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        raise ValueError(err_msg_frmt.format(attr, dtype))
                else:
                    enc_value = str(value)
            else:
                err_msg = "Attribute '{}' is not given in the reference metadata.".format(attr)
                raise KeyError(err_msg)
        else:
            enc_value = value

        return enc_value

    def __and__(self, other):
        """ Finds common metadata attributes among the two metadata classes. """
        common_keys = self._meta.keys() & other._meta.keys()
        common_metadata = dict()
        common_ref_metadata = dict()
        common_ref_metadata['Metadata'] = dict()
        common_ref_metadata['Expected_value'] = dict()
        for common_key in common_keys:
            common_metadata[common_key] = self._meta[common_key]
            ref_meta = self._ref_meta['Metadata'].get(common_key)
            if ref_meta is not None:
                common_ref_metadata['Metadata'][common_key] = ref_meta
            ref_exp_value = self._ref_meta['Expected_value'].get(common_key)
            if ref_exp_value is not None:
                common_ref_metadata['Expected_value'][common_key] = ref_exp_value

        return MetaData(common_metadata, common_ref_metadata)

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

