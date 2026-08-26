import subprocess
import sys
import os
import re
import ast


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
        elif path.endswith(('.html', '.htm')):
            # Basic HTML validation - check for balanced tags (simplified)
            open_tags = content.count('<')
            close_tags = content.count('>')
            if open_tags != close_tags:
                return False, f"Syntax Error in {path}: Unbalanced HTML tags"
        elif path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            # Basic JS/TS validation - check for balanced braces and brackets
            if content.count('{') != content.count('}') or content.count('[') != content.count(']'):
                return False, f"Syntax Error in {path}: Unbalanced braces/brackets"
        elif path.endswith('.css'):
            # Basic CSS validation - check for balanced braces
            if content.count('{') != content.count('}'):
                return False, f"Syntax Error in {path}: Unbalanced CSS braces"
    return True, ""


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