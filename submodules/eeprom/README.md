# Eeprom

## Development

To create a yaml file from the bytes stored in the eeprom, run the following (default eeprom address is 0x50 and default yaml file to write to is new_yaml.yaml():
```
python3 -c "import eeprom; eeprom.start()"  # Run eeprom/__init__.start()
```
To store a yaml file in the eeprom, run the following (default eeprom address is 0x50 and default yaml file to read from is config.yaml():
```
python3 -c "import eeprom; eeprom.store_yaml()"  # Run eeprom/__init__.store_yaml()
```
Upcoming updates:
 - Easier variable storage and access
 - Count feature to detect number of variables stored
 - All code on one file
 
 Notes:
  - Data is seperated by "!"
  - Yaml files must not include double quotes
