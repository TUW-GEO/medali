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
Test functions in the metadata base .
"""

import os
import unittest
import datetime

from src.medali.metadata_base import metadata

class MetadataReadTest(unittest.TestCase):
    """
    Test reading of all available config files.
    """

    def test_configs_read(self):
        """
        Test reading all available config files and filling null values.
        """
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "medali",
                                   "configs")

        config_files = os.listdir(config_path)

        print('Checked config files:')

        for f in config_files:
            print(f)
            config_filepath = os.path.join(config_path, f)
            meta = metadata(config_file=config_filepath)
            meta.fill_null_values()
            self.assertEqual(meta.meta['Metadata'].keys(), meta.meta['Expected_value'].keys())

class MetadataModificationCheckTest(unittest.TestCase):
    """
    Test reading, writing and checking of template metadata.
    """

    def read_template(self):
        """
        Read template config file.
        """
        config_filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "medali",
                                   "templates", "metadata_config_template.ini")

        meta = metadata(config_file=config_filepath)

        return meta

    def fill_values(self):
        """
        Fill default values for metadata check.
        """
        meta = self.read_template()
        meta.set_metadata_item('datetime_type', datetime.datetime(year=2020, month=12, day=12,
                                                                  hour=12, minute=20, second=10))
        meta.set_metadata_item('boolean_type', False)
        meta.set_metadata_item('number_type', 1.2)
        meta.set_metadata_item('integer_type', 1)
        meta.set_metadata_item('string_general', 'abc')
        meta.set_metadata_item('string_list', 'V3')
        meta.set_metadata_item('string_pattern', 'Pattern01')

        return meta

    def test_datetime_conversion(self):
        """
        test datatype filling and conversion to string.
        """
        meta = self.read_template()
        meta.set_metadata_item('datetime_type', datetime.datetime(year = 2020, month = 12, day = 12,
                                                                     hour = 12, minute = 20, second = 10))
        self.assertEqual(meta.meta['Metadata']['datetime_type'], '2020-12-12 12:20:10')

    def test_boolean_conversion(self):
        """
        test boolean filling and conversion to string.
        """
        meta = self.read_template()
        meta.set_metadata_item('boolean_type', False)
        self.assertEqual(meta.meta['Metadata']['boolean_type'], 'False')

    def test_number_conversion(self):
        """
        test number filling and conversion to string.
        """
        meta = self.read_template()
        meta.set_metadata_item('number_type', 1.2)
        self.assertEqual(meta.meta['Metadata']['number_type'], '1.2')

    def test_integer_conversion(self):
        """
        test integer filling and conversion to string.
        """
        meta = self.read_template()
        meta.set_metadata_item('integer_type', 1)
        self.assertEqual(meta.meta['Metadata']['integer_type'], '1')

    def test_string_fill(self):
        """
        test string filling and conversion to string.
        """
        meta = self.read_template()
        meta.set_metadata_item('string_general', 'abc')
        self.assertEqual(meta.meta['Metadata']['string_general'], 'abc')

    def test_metadata_check(self):
        """
        test check metadata function.
        """

        meta = self.fill_values()
        tags_dict = {'datetime_type': '2020-12-12 12:20:10',
                     'string_pattern': 'Pattern01',
                     'string_general': 'abc',
                     'integer_type': '1',
                     'number_type': '1.2',
                     'string_list': 'V3',
                     'boolean_type': 'False'}
        missing_keys, suspiccious_keys, empty_keys = meta.check_metadata(tags_dict)
        self.assertEqual([missing_keys, suspiccious_keys, empty_keys], [[],[],[]])

if __name__ == '__main__':
    unittest.main()