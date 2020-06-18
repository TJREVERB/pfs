import os


class AntennaDeployedActuateTask:
    FILE_PATH = os.path.join(os.environ["HOME"], 'antenna_deployed')

    def __init__(self):
        self.run = False

    def execute(self):
        if not self.run:
            return

        self.run = False

        file = open(self.FILE_PATH, "w")
        file.close()
