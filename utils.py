import subprocess
import sys
import os

class CodeRunner:
    @staticmethod
    def run_with_timeout(code, timeout=10):
        """Runs Python code safely in an isolated subprocess."""
        if not code.strip():
            return "Error: No code provided."

        file_name = "temp_exec.py"
        
        # 1. Write the code to a temporary file
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            # 2. Run the code using the server's Python executable
            result = subprocess.run(
                [sys.executable, file_name],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # 3. Check if execution was successful (Return code 0 means no crashes)
            if result.returncode == 0:
                output = result.stdout.strip()
                # Include the word "Passed" so the Tester node knows it was successful
                return f"Execution Passed. Output:\n{output}" if output else "Execution Passed (No Output)."
            else:
                return f"Runtime Error:\n{result.stderr.strip()}"

        except subprocess.TimeoutExpired:
            return "Timeout Error: Code execution took too long (> 10 seconds)."
        except Exception as e:
            return f"System Error: {str(e)}"
        finally:
            # 4. Clean up the temp file
            if os.path.exists(file_name):
                os.remove(file_name)