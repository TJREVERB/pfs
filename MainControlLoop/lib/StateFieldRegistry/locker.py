from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField
from MainControlLoop.tasks.DownLinkProducer import DownLinkProducer


class StateFieldRegistryLocker:

   def __init__(self):
      self.locker = []

   def store(self, state_field_registry):
      """
      Adds a StateFieldRegistry to the locker as a tuple: (Timestamp, Dump)
      Preserves ordering by timestamp (least to greatest, oldest to newest)
      :param state_field_registry: StateFieldRegistry to add to Locker
      """
      sfrTuple = (state_field_registry.get(StateField.SYS_TIME), DownLinkProducer.create_dump(state_field_registry))    # Creates a tuple with sfrTuple[0] = timestamp, sfrTuple[1] = dump of SFR
      index = len(self.locker)
      for i in range(len(self.locker)):
         if self.locker[i][0] > sfrTuple[0]:
            index = i
            break
      self.locker = self.locker[:index] + [sfrTuple] + self.locker[index:]

   def find(self, timeReq):
      """
      Finds the StateFieldRegistry stored in the locker with timestamp closest to 'timeReq'
      :param timeReq: Timestamp requested
      """
      if len(self.locker) == 0:
         return None
      else:
         return min(range(len(self.locker)), key=lambda i: abs(self.locker[i][0]-timeReq))


locker = StateFieldRegistryLocker()
state_field_registry = StateFieldRegistry()
locker.store(state_field_registry)