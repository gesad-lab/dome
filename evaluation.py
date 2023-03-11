import unittest
import test_evaluation

suite = unittest.TestLoader().loadTestsFromModule(test.TestT2S)
unittest.TextTestRunner().run(suite)
