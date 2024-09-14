# run_tests.py
import unittest

if __name__ == '__main__':
    # Discover and run all tests in the 'tests' folder
    tests = unittest.TestLoader().discover('tests')
    test_runner = unittest.TextTestRunner()
    test_runner.run(tests)
