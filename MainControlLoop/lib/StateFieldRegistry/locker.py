from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField
from MainControlLoop.tasks.DownLinkProducer import DownLinkProducer


class StateFieldRegistryLocker:

   def __init__(self):
      self.locker = []

   def store(self, state_field_registry):
      """
      Adds a StateFieldRegistry to the locker as a tuple: (Timestamp, Corresponding Dump)
      Preserves ordering by timestamp (least to greatest, oldest to newest)
      :param state_field_registry: StateFieldRegistry to add to Locker
      """

      sfrTuple = (state_field_registry.get(StateField.SYS_TIME), DownLinkProducer.create_dump(state_field_registry))    # Creates a tuple with sfrTuple[0] = timestamp, sfrTuple[1] = dump of SFR
      if len(self.locker) == 0:
         self.locker.append(sfrTuple)
      else:
         index = len(self.locker)
         for i in range(len(self.locker)):
            if self.locker[i][0] >= sfrTuple[0]:
               index = i
               break
         self.locker.insert(index, sfrTuple)

   def find(self, timeReq):
      """
      Finds the StateFieldRegistry stored in the locker with timestamp closest to 'timeReq'
      :param timeReq: Timestamp requested
      """

      if len(self.locker) > 0:
         for i in range(len(self.locker)):
            if timeReq == self.locker[i][0]:
               return self.locker[i][1]
            elif timeReq >= self.locker[i][0]:
               downDiff = timeReq - self.locker[i][0]
               upDiff = self.locker[i+1][0] - timeReq
               if downDiff < upDiff:
                  return self.locker[i][1]
               else:
                  return self.locker[i+1][1]
         return self.locker[-1][1]
      else:
         return None

locker = StateFieldRegistryLocker()
state_field_registry = StateFieldRegistry()
locker.store(state_field_registry)