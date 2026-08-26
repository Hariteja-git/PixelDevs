import subprocess
import sys
import os
import re
import ast
import tempfile
import shutil
from dotenv import load_dotenv

load_dotenv()  # This loads variables from .env into os.environ


def extract_files_from_artifact(text: str) -> dict[str, str]:
    """Parse XML artifact blocks and return a dict mapping file paths to content."""
    pattern = r'<file path="([^"]+)">\n?(.*?)\n?</file>'
    matches = re.findall(pattern, text, re.DOTALL)
    result = {}
    for path, content in matches:
        normalized_path = path.strip()
        if normalized_path:
            result[normalized_path] = content.strip('\n')
    return result


def validate_code_syntax(files: dict[str, str]) -> tuple[bool, str]:
    """Validate syntax of code files. Returns (is_valid, error_message)."""
    for path, content in files.items():
        if path.endswith('.py'):
            try:
                ast.parse(content)
            except SyntaxError as e:
                return False, f"Syntax Error in {path}: {e.msg} (line {e.lineno})"
    return True, ""


def run_in_e2b_sandbox(files: dict[str, str], entrypoint: str) -> tuple[int, str, str]:
    """Execute files in E2B cloud sandbox. Falls back to local subprocess if E2B_API_KEY is missing."""
    e2b_api_key = os.environ.get("E2B_API_KEY")
    if not e2b_api_key:
        return run_local_fallback(files, entrypoint)

    try:
        from e2b_code_interpreter import Sandbox
    except ImportError:
        return run_local_fallback(files, entrypoint)

    try:
        sandbox = Sandbox(api_key=e2b_api_key, timeout=20)
        try:
            # Write all files to sandbox
            for path, content in files.items():
                sandbox.files.write(path, content)
            # Execute entrypoint
            execution = sandbox.commands.run(entrypoint, timeout=20)
            return execution.exit_code, execution.stdout, execution.stderr
        finally:
            sandbox.kill()
    except Exception as e:
        return -1, "", f"E2B Sandbox Error: {str(e)}"


def run_local_fallback(files: dict[str, str], entrypoint: str) -> tuple[int, str, str]:
    """Local subprocess fallback when E2B is unavailable."""
    temp_dir = tempfile.mkdtemp()
    try:
        # Write all files
        for path, content in files.items():
            file_path = os.path.join(temp_dir, path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        # Run entrypoint
        result = subprocess.run(
            entrypoint.split(),
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=20
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout Error: Code execution took too long (> 20 seconds)."
    except Exception as e:
        return -1, "", f"Local Fallback Error: {str(e)}"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def apply_search_replace_patch(original: str, search_block: str, replace_block: str) -> str:
    """Apply a localized search-and-replace patch to the original content."""
    if search_block in original:
        return original.replace(search_block, replace_block, 1)
    return original


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