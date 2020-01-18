from MainControlLoop.lib.isisants import isisants

from MainControlLoop.lib.devices import Device


class AntennaDeployer(Device):

    def __init__(self):
        super().__init__("antenna_deployer")

    def deploy(self):

        isisants.py_k_ants_init(b"/dev/i2c-1", 0x31, 0x32, 4, 10)

        # Arms device
        isisants.py_k_ants_arm()

        # Deploy
        isisants.py_k_ants_deploy(0, False, 5)
        isisants.py_k_ants_deploy(1, False, 5)
        isisants.py_k_ants_deploy(2, False, 5)
        isisants.py_k_ants_deploy(3, False, 5)

