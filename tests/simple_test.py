import unittest

class TddInPythonExample(unittest.TestCase):

    def test_calculator_add_method_returns_correct_result(self):
        result = 2 + 2
        self.assertEqual(4, result)


if __name__ == '__main__':
    unittest.main()
