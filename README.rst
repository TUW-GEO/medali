======
medali
======


*medali* stands for **ME**\ ta\ **DA**\ ta **LI**\ brary and is responsible for parsing, tagging and interpreting product metadata. 


Description
===========

The metadata is defined using configuration file. Configurtion files are stored in the corresponding folder in src/medali/lib named after the metadata version. Current functionality includes:
  * creating metadata object using the configuration file
  * setting and encoding (from given dataformat to string) the given metadata attributes
  * returning and decoding (from string to given dataformat) the given metadata attributes
  * checking if given metadata meet the criteria given in config file (is within a list of allowed values, contain specified string)
  
Including new data types
========================

Template configuration file can be found in templates folder. Specify all needed tags and their dataformat (currently supported: string, boolean, datatime, integer, number) in the Metadata section of the config file. Expected_value part should contain only those metadata attributes that need to meet some specific criteria (be value within a list or contain a specific pattern). Config files are named according to their version and placed in a subfolder in in src/medali/lib named after the datatype.



