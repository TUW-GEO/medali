# Copyright (c) 2018, TU Wien, Department of Geodesy and Geoinformation
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
Reading and modification of the metadata

"""

from configparser import ConfigParser
import numbers
import datetime
import os
from dateutil.parser import parse
import re

class metadata:
    def __init__(self, config_file=None, data_id=None, version_id=None):
        self.meta = read_config(config_file=config_file, data_id=data_id, version_id=version_id)

    def fill_null_values(self):
        for key in self.meta['Metadata']:
            if self.meta['Metadata'][key] in ('string', 'integer', 'boolean', 'datetime', 'number'):
                self.meta['Metadata'][key] = 'null'

    def set_metadata_item(self, key, value):
        if self.meta['Metadata'][key] == 'string': # todo add check for the type of the actual data
            if isinstance(value, str):
                self.meta['Metadata'][key] = value
            else:
                err_msg = "MEDALI: Metadata information for key '{}' has to be string".format(key)
                raise ValueError(err_msg)
        elif self.meta['Metadata'][key] == 'boolean':
            if isinstance(value, bool):
                self.meta['Metadata'][key] = str(value)
            else:
                err_msg = "MEDALI: Metadata information for key '{}' has to be boolean".format(key)
                raise ValueError(err_msg)
        elif self.meta['Metadata'][key]  == 'integer':
            if isinstance(value, int):
                self.meta['Metadata'][key] = str(value)
            else:
                err_msg = "MEDALI: Metadata information for key '{}' has to be integer".format(key)
                raise ValueError(err_msg)
        elif self.meta['Metadata'][key]  == 'number':
            if isinstance(value, numbers.Number):
                self.meta['Metadata'][key] = str(value)
            else:
                err_msg = "MEDALI: Metadata information for key '{}' has to be number".format(key)
                raise ValueError(err_msg)
        elif self.meta['Metadata'][key]  == 'datetime':
            if isinstance(value, datetime.datetime):
                self.meta['Metadata'][key] = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                err_msg = "MEDALI: Metadata information for key '{}' has to be datetime object".format(key)
                raise ValueError(err_msg)
        else:
            self.meta['Metadata'][key] = str(value)

    def check_metadata(self, meta_dict):
        """
            Checks if given file contains metadata in compliance with
            corresponding metadata config file.

            Parameters
            ----------
            meta_dict: dictionary
                dictionary containing metadata keys and values

            Returns
            ----------
            missing_keys: list
                list of metadata keys that are missing in dataset
                when compared with config file
            suspiccious_keys: list
                list of metadata keys that have suspiccious values
                when compared to rules defined in comfg file
            empty_keys: list
                list of metadata keys that cntain 'null' value
            """

        if not isinstance(meta_dict, dict):
            err_msg = "meta_dict has to be dictionary."
            raise IOError(err_msg)
        template = self.meta['Expected_value']

        missing_keys = []
        suspiccious_keys = []
        empty_keys = []
        for key in template:
            if key not in meta_dict.keys():
                missing_keys.append(key)
            elif meta_dict[key] == 'null':
                empty_keys.append(key)
            elif isinstance(template[key], list):
                if meta_dict[key] not in template[key]:
                    suspiccious_keys.append(key)
            elif template[key] in ('integer', 'number'):
                if not meta_dict[key].replace('.','',1).isnumeric():
                    suspiccious_keys.append(key)
            elif template[key] == 'boolean':
                if meta_dict[key] not in ['False', 'True']:
                    suspiccious_keys.append(key)
            elif template[key] == 'datetime':
                if not isdate(meta_dict[key]):
                    suspiccious_keys.append(key)
            elif template[key].startswith('pattern'):
                value = template[key].replace(', ', ',')
                value = value.split(',')
                pattern = value[1]
                if not re.search(pattern, meta_dict[key]):
                    suspiccious_keys.append(key)
            elif template[key] == 'string':
                dummy=1

            else:
                print(key)

        return missing_keys, suspiccious_keys, empty_keys

def read_config(config_file=None, data_id=None, version_id=None):
    """
    Parse a metadata config file.

    Parameters
    ----------
    config_file: string
        Filename of the config file. Either config_file or
        data_id and version_id needs to be set.
    data_id: string
        id of the data for which the metadata config file
        should be loaded (placed in config folder).
    version_id: string
        id of the data for which the metadata config file
    """
    if not config_file:
        if data_id and version_id:
            cfg_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs",
                                        data_id + '_' + version_id + '.ini')
        else:
            err_msg = "Either metadata config_file path or data_id and version_id needs to be set."
            raise IOError(err_msg)
    else: cfg_filepath = config_file

    if not os.path.exists(cfg_filepath):
        err_msg = "'metadata_config.ini' file is not available."
        raise IOError(err_msg)

    config = ConfigParser()
    config.optionxform = str
    config.read(cfg_filepath)

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
    try:
        parse(string)
        return True
    except ValueError:
        return False

