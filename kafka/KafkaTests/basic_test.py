'''
Created on Jun 23, 2017
@author: GDE
'''
import unittest
import cast.analysers.test
class KafkaTest(unittest.TestCase):
    def testRegisterPlugin(self):
        analysis = cast.analysers.test.JEETestAnalysis()
        analysis.add_selection("Tests")
        analysis.set_verbose()
        analysis.run()
if __name__ == "__main__":
    unittest.main()


