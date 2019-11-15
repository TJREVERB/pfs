from . import isisants
from helpers import log


class AntennaDeployer(Submodule):

    def __init__(self, config: dict):
        self.config = config
        self.modules = dict()

    def has_module(self, module_name):
        return module_name in self.modules and self.modules[module_name] is not None

    def set_modules(self, dependencies: dict):
        self.modules = dependencies

    def start(self):
        # Initialize connection with device
        isisants.py_k_ants_init(b"/dev/i2c-1", 0x31, 0x32, 4, 10)

        # Arms device
        isisants.py_k_ants_arm()

        # Deploy
        isisants.py_k_ants_deploy(self.config['antenna']['ANT_1'], False, 5)
        isisants.py_k_ants_deploy(self.config['antenna']['ANT_2'], False, 5)
        isisants.py_k_ants_deploy(self.config['antenna']['ANT_3'], False, 5)
        isisants.py_k_ants_deploy(self.config['antenna']['ANT_4'], False, 5)
        
        if self.has_module("telemetry"):
            self.modules["telemetry"].enqueue(
                log.Log(
                    sys_name="antenna_deployer",
                    lvl='INFO',
                    msg="antenna deployed"
                )
            )
        # No need for RuntimeError for the process will terminate