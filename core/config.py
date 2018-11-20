"""
Module to handle persistent config.  Values will be loaded _once_ from default.yml and on _every_ boot from _config.yml.
Values are saved back out to config.yml whenever a value is changed.
The config object from `core.config` will be an instance of ConfigDictionary, and can be accessed either by indexing as
usual (i.e. config['aprs']['bperiod']) or by using dot notation (config.aprs.bperiod).
"""
