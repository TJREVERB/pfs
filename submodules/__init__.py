class Submodule:

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.modules = dict()
        self.processes = dict()

    def start(self):
        raise NotImplementedError

    def enter_low_power_mode(self):
        raise NotImplementedError

    def enter_normal_mode(self):
        raise NotImplementedError

    def set_modules(self, dependencies):
        self.modules = dependencies

    def has_module(self, module_name):
        return module_name in self.modules and self.modules[module_name] is not None

    def get_module_or_raise_error(self, module_name):
        if module_name in self.modules and self.modules[module_name] is not None:
            return self.modules[module_name]
        else:
            raise RuntimeError(f"[{self.name}]:[{module_name}] not found")
