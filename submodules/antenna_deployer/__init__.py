from helpers import log
from submodules.submodule import Submodule

from . import isisants


class AntennaDeployer(Submodule):
    """
    Submodule class that interfaces with the ISIS Antenna Deployer
    """
    def __init__(self, config: dict):
        """
        Instantiates a new AntennaDeployer instance
        :param config: dictionary of configuration data
        """
        Submodule.__init__(self, name="antenna_deployer", config=config)

    def start(self) -> None:
        """
        Deploys the ISIS Antenna via I2C
        :return: None
        """
        # Initialize connection with device
        isisants.py_k_ants_init(b"/dev/i2c-1", 0x31, 0x32, 4, 10)

        # Arms device
        isisants.py_k_ants_arm()

        # Deploy
        isisants.py_k_ants_deploy(self.config['antenna']['ANT_1'], False, 5)
        isisants.py_k_ants_deploy(self.config['antenna']['ANT_2'], False, 5)
        isisants.py_k_ants_deploy(self.config['antenna']['ANT_3'], False, 5)
        isisants.py_k_ants_deploy(self.config['antenna']['ANT_4'], False, 5)

        # No need for RuntimeError for the process will terminate
        if self.has_module("telemetry"):
            self.modules["telemetry"].enqueue(
                log.Log(
                    sys_name="antenna_deployer",
                    lvl='INFO',
                    msg="antenna deployed"
                )
            )

    def enter_low_power_mode(self) -> None:
        """
        Empty because Antenna Deployer does not react to changes in Modes
        :return: None
        """
        pass  # Antenna Deployer has no-op

    def enter_normal_mode(self) -> None:
        """
        Empty because Antenna Deployer does not react to changes in Modes
        :return: None
        """
        pass  # Antenna Deployer has no-op
