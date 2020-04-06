import unittest

import microservice_v1

class Test(unittest.TestCase):

    def integrationTest(self):

       result = microservice_v1.completeModel(5, '/tmp/workflow/arimaHum.pkl', '/tmp/workflow/arimaTemp.pkl')
       self.assertEqual(len(result),5,"It has to be as many elements as hours")


if __name__ == '__main__':
    unittest.main()