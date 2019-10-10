from . import isisants
from core import config

def start():
    # Initiate connection with the device
    isisants.py_k_ants_init(b"/dev/i2c-1", 0x31, 0x32, 4, 10)

    # Arms the device
    isisants.py_k_ants_arm()

    # Run the deploy methods
    isisants.py_k_ants_deploy(config['antenna']['ANT_1'], False, 5)
    isisants.py_k_ants_deploy(config['antenna']['ANT_2'], False, 5)
    isisants.py_k_ants_deploy(config['antenna']['ANT_3'], False, 5)
    isisants.py_k_ants_deploy(config['antenna']['ANT_4'], False, 5)
