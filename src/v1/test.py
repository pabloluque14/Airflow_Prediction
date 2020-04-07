# -*- coding: utf-8 -*-

import unittest

import microservice_v1

class Test(unittest.TestCase):

    # the name of the test function must start with "test_" 
    def test_integration(self):
       result = microservice_v1.completeModel(5, '/tmp/workflow/v1/arimaHum.pkl', '/tmp/workflow/v1/arimaTemp.pkl')
       self.assertEqual(len(result),5,"There has to be as many elements as hours")


if __name__ == '__main__':
    unittest.main()
    