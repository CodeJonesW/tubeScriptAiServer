# run_tests.py
import unittest

if __name__ == '__main__':
    # Discover and run all tests in the 'tests' folder
    try:
        print("Discovering and running all tests in the 'tests' folder...")
        tests = unittest.TestLoader().discover('tests')
        test_runner = unittest.TextTestRunner(verbosity=2)
        result = test_runner.run(tests)
        
        # Summarize test results
        if result.wasSuccessful():
            print(f"\nAll tests passed ({result.testsRun} tests run).")
        else:
            print(f"\nTest run failed. {len(result.failures)} failures, {len(result.errors)} errors.")
    
    except Exception as e:
        print(f"Error occurred while running tests: {str(e)}")
