from .create_yaml import make_file
from .eeprom_write_yaml import write_yaml
from .eeprom_read_yaml import read_yaml

def start():
  make_file()

def store_yaml(address=0x50, filename="config.yaml"):
  write_yaml(address, filename)
  
def regen_yaml(address=0x50, size=1024):
  read_yaml(address, size)
  
def count():
  pass
