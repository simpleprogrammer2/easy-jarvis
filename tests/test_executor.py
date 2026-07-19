from src.executor import Executor


def test_executor_basic_command():
    executor = Executor()
    # Test a simple echo command
    output = executor.execute("echo 'hello world'")
    assert "hello world" in output


def test_executor_invalid_command():
    executor = Executor()
    # Test a command that should fail
    output = executor.execute("nonexistentcommand")
    assert "not found" in output.lower() or "not recognized" in output.lower()
