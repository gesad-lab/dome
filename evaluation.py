import unittest
import test_evaluation

suite = unittest.TestLoader().loadTestsFromModule(test_evaluation.TestT2S)
unittest.TextTestRunner().run(suite)
