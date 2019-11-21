from submodules import Submodule

class FakeCommandIngest(Submodule.Submodule):
    """
    Fake command ingest. Doesn't actually do anything, but just prints received commands to stdout.
    """

    def __init__(self, config):
        Submodule.Submodule.__init__(self, "command_ingest", config)

    def enqueue(self, cmd):
        print("CI: Received command")
        print(cmd)