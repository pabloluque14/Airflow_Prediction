# -*- coding: utf-8 -*-

import unittest

import microservice_v2

class Test(unittest.TestCase):

    # the name of the test function must start with "test_"
    def test_integration(self):
       result = microservice_v2.completeModel(5, '/tmp/workflow/v2/smoothHum.pkl', '/tmp/workflow/v2/smoothTemp.pkl')
       self.assertEqual(len(result),5,"There has to be as many elements as hours")



if __name__ == '__main__':
    unittest.main()