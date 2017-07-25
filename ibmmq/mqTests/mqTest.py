'''
Created on Jul 13, 2017
@author: GSO
'''
import unittest
import cast.analysers.test

class IBMMQTest(unittest.TestCase):
    def testRegisterPlugin(self):
        analysis = cast.analysers.test.JEETestAnalysis()
        analysis.add_selection("Tests")
        analysis.set_verbose()
        analysis.run()
if __name__ == "__main__":
    unittest.main()