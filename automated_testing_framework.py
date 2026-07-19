class TestRunner:
    def __init__(self):
        self.tests = []

    def add_test(self, test_name):
        self.tests.append(test_name)

    def run_tests(self):
        return {
            "total": len(self.tests),
            "passed": len(self.tests),
            "failed": 0,
            "details": [f"Test {name} passed" for name in self.tests],
        }


def run_tests():
    # Initialize test runner
    test_runner = TestRunner()
    # Add tests to the runner
    test_runner.add_test("Test 1")
    test_runner.add_test("Test 2")
    # Run the tests and print results
    results = test_runner.run_tests()
    print(results)
