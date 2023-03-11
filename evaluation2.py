import unittest
import test

suite = unittest.TestLoader().loadTestsFromModule(test.TestT2S)
unittest.TextTestRunner().run(suite)
