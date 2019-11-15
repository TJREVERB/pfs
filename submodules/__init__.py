class Submodule:

    def start(self):
        raise NotImplementedError

    def enter_low_power_mode(self):
        raise NotImplementedError

    def enter_normal_mode(self):
        raise NotImplementedError

    def set_modules(self, **kwargs):
        raise NotImplementedError

    def has_module(self, module_name):
        raise NotImplementedError

    def get_module_or_raise_error(self, module_name):
        raise NotImplementedError