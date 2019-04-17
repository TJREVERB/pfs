from pathlib import Path
from eeprom_read_yaml import read_yaml
import yaml

def make_file():
	stream = open("new_yaml.yaml", "w")
	yaml.dump(read_yaml(), stream)
	print(yaml.dump(read_yaml()))

if __name__ == "__main__":
	make_file()
