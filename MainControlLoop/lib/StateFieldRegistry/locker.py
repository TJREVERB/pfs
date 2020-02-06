from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField
from MainControlLoop.tasks.DownLinkProducer import DownLinkProducer


class StateFieldRegistryLocker:

    def __init__(self):
        self.locker = []

    def store(self, state_field_registry: StateFieldRegistry):
        """
        Adds a StateFieldRegistry to the locker as a tuple: (Timestamp, Dump)
        Preserves ordering by timestamp (least to greatest, oldest to newest)
        :param state_field_registry: StateFieldRegistry to add to Locker
        """
        if not isinstance(state_field_registry, StateFieldRegistry):
            return

        # Creates a tuple with locker_item[0] = timestamp, locker_item[1] = dump of SFR
        locker_item = (state_field_registry.get(StateField.SYS_TIME), DownLinkProducer.create_dump(
            state_field_registry))
        index = len(self.locker)
        for i in range(len(self.locker)):
            if self.locker[i][0] > locker_item[0]:
                index = i
                break
        self.locker = self.locker.insert(index, locker_item)

    def find(self, timestamp: float):
        """
        Finds the StateFieldRegistry (Timestamp, dump) stored in the locker with timestamp closest to 'timeReq'
        :param timestamp: Timestamp requested
        """
        if not isinstance(timestamp, float):
           return

        if len(self.locker) == 0:
            return

        return self.locker[min(range(len(self.locker)), key=lambda i: abs(self.locker[i][0] - timestamp))]
