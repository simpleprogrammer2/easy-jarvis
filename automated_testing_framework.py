def run_tests():
    # Initialize test runner
    test_runner = TestRunner()
    # Add tests to the runner
    test_runner.add_test('Test 1')
    test_runner.add_test('Test 2')
    # Run the tests and print results
    results = test_runner.run_tests()
    print(results)
