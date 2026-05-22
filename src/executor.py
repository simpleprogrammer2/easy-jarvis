import subprocess
import os

class Executor:
    def __init__(self):
        # Proactive Safety Gate: Block obviously destructive commands
        self.blocked_patterns = [
            "rm -rf /", "mkfs", "dd if=", "> /dev/sda", 
            ":(){ :|:& };:", "chmod -R 777 /"
        ]

    def execute(self, command: str) -> str:
        """Safely executes a shell command and returns the output."""
        print(f"[*] easy-jarvis Executor: Analyzing '{command}'...")
        
        # 1. Safety Check
        for pattern in self.blocked_patterns:
            if pattern in command:
                return f"[!] Safety Block: The command '{command}' contains a restricted pattern '{pattern}'."

        # 2. Execution
        try:
            # We use shell=True to allow for pipes and complex commands, 
            # but the safety gate above mitigates risk.
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            output = result.stdout
            error = result.stderr
            
            if result.returncode == 0:
                return output if output else "[Success: No Output]"
            else:
                return f"[Error (Code {result.returncode})]: {error}"
                
        except subprocess.TimeoutExpired:
            return "[!] Error: Command timed out after 60 seconds."
        except Exception as e:
            return f"[!] Unexpected Execution Error: {str(e)}"

if __name__ == "__main__":
    ex = Executor()
    print(ex.execute("ls -la"))
    print(ex.execute("echo 'Hello JARVIS'"))
    print(ex.execute("rm -rf /")) # Should be blocked
