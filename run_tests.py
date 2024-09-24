# run_tests.py
import unittest
import sys

if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            # If arguments are provided, use them to run specific tests
            test_names = sys.argv[1:]
            print(f"Running specified tests: {', '.join(test_names)}")
            suite = unittest.TestLoader().loadTestsFromNames(test_names)
        else:
            # If no arguments, discover and run all tests
            print("Discovering and running all tests in the 'tests' folder...")
            suite = unittest.TestLoader().discover('tests')

        test_runner = unittest.TextTestRunner(verbosity=2)
        result = test_runner.run(suite)
        
        if result.wasSuccessful():
            print(f"\nAll tests passed ({result.testsRun} tests run).")
        else:
            print(f"\nTest run failed. {len(result.failures)} failures, {len(result.errors)} errors.")
    
    except Exception as e:
        print(f"Error occurred while running tests: {str(e)}")
