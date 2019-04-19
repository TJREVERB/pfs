from create_yaml import make_file

def start():
  make_file()

def store_yaml(address=0x50, filename="config.yaml"):
  write_yaml(address, filename)
  
def regen_yaml(address=0x50, size=1024):
  read_yaml(address, size)
  
def count(address=0x50):
  read_yaml(address, 16384)

