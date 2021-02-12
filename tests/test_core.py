# Copyright (c) 2021, Vienna University of Technology (TU Wien), Department
# of Geodesy and Geoinformation (GEO).
# All rights reserved.
#
# All information contained herein is, and remains the property of Vienna
# University of Technology (TU Wien), Department of Geodesy and Geoinformation
# (GEO). The intellectual and technical concepts contained herein are
# proprietary to Vienna University of Technology (TU Wien), Department of
# Geodesy and Geoinformation (GEO). Dissemination of this information or
# reproduction of this material is forbidden unless prior written permission
# is obtained from Vienna University of Technology (TU Wien), Department of
# Geodesy and Geoinformation (GEO).

"""
Tests metadata base class.

"""

import os
import glob
import unittest
import datetime

from src.medali.core import MetaData


class MetadataConfigReadTest(unittest.TestCase):
    """
    Tests reading of all available config files.

    """

    def test_configs_read(self):
        """
        Test reading all available config files and filling null values.

        """
        root_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "medali"))
        lib_path = os.path.join(root_dirpath, "lib")

        product_names = os.listdir(lib_path)
        cfg_filepaths = []
        for product_name in product_names:
            product_dirpath = os.path.join(lib_path, product_name)
            cfg_filepaths.extend(glob.glob(os.path.join(product_dirpath, "*.ini")))

        for cfg_filepath in cfg_filepaths:
            metadata = MetaData.from_cfg_file({}, cfg_filepath)
            self.assertEqual(metadata._meta.keys(), metadata._ref_meta['Metadata'].keys())
            self.assertEqual(metadata._meta.keys(), metadata._ref_meta['Expected_value'].keys())


class MetadataConversionCheckTest(unittest.TestCase):
    """
    Test reading, checking and converting metadata with respect to the reference metadata.

    """

    def setUp(self):
        """
        Reads template config metadata file and creates a `MetaData` instance.

        """
        test_data_dirpath = os.path.join(os.path.dirname(__file__), "test_data")
        cfg_filepath = os.path.join(test_data_dirpath, "cfg_template.ini")

        self.metadata = MetaData.from_cfg_file({}, cfg_filepath)
        self.metadata['datetime_type'] = datetime.datetime(2020, 12, 12, 12, 20, 10)
        self.metadata['boolean_type'] = False
        self.metadata['number_type'] = 1.2
        self.metadata['integer_type'] = 1
        self.metadata['string_general'] = 'abc'
        self.metadata['string_list'] = 'V3'
        self.metadata['string_pattern'] = 'Pattern01'

    def test_set_metadata_attributes(self):
        """
        Tests metadata item setting.

        """
        metadata_should = {'datetime_type': '2020-12-12 12:20:10',
                           'string_pattern': 'Pattern01',
                           'string_general': 'abc',
                           'integer_type': '1',
                           'number_type': '1.2',
                           'string_list': 'V3',
                           'boolean_type': 'False'}

        self.assertDictEqual(metadata_should, self.metadata._meta)

    def test_get_metadata_attributes(self):
        """ Tests value decoding when accessing metadata attributes. """

        assert self.metadata['datetime_type'] == datetime.datetime(2020, 12, 12, 12, 20, 10)
        assert not self.metadata['boolean_type']
        assert self.metadata['number_type'] == 1.2
        assert self.metadata['integer_type'] == 1
        assert self.metadata['string_general'] == 'abc'
        assert self.metadata['string_list'] == 'V3'
        assert self.metadata['string_pattern'] == 'Pattern01'

    def test_metadata_check(self):
        """
        Tests checking of external metadata.

        """

        metadata = {'datetime_type': '2020-12-12 12:20:10',
                    'string_pattern': 'null',
                    'integer_type': '1',
                    'number_type': 'haha',
                    'string_list': 'V3',
                    'boolean_type': 'False'}
        missing_keys, suspicious_keys, empty_keys = self.metadata.check_metadata(metadata)
        self.assertEqual([missing_keys, suspicious_keys, empty_keys], [['string_general'],
                                                                       ['number_type'],
                                                                       ['string_pattern']])


if __name__ == '__main__':
    unittest.main()
