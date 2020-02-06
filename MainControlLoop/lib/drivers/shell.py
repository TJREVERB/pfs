import unittest
from Iridium import Iridium


class TestIridium(unittest.TestCase):
   # Configure Iridium Driver
   def configure(self):
      self.driver = Iridium()
      self.assertTrue(self.driver.functional())

   # Test writing an arbitrary command
   def test_write(self):
      resp, success = self.driver.write('do_stuff')
      print(resp)
      self.assertTrue(success)

   # Test reading one byte
   def test_read(self):
      resp = self.driver.read()
      print(resp)
      self.assertTrue(resp)


if __name__ == '__main__':
   unittest.main()
