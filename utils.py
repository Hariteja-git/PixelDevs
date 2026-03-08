import sys
import io
import contextlib
import threading
import queue

class CodeRunner:
    @staticmethod
    def run_with_timeout(code, timeout=5):
        """Runs code in a separate thread with a timeout."""
        result_queue = queue.Queue()

        def target():
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                    exec_globals = {}
                    exec(code, exec_globals)
                output = stdout_capture.getvalue() + stderr_capture.getvalue()
                result_queue.put(output if output else "Code Ran Successfully (No Output)")
            except Exception as e:
                result_queue.put(f"Runtime Error: {str(e)}")

        t = threading.Thread(target=target)
        t.daemon = True 
        t.start()
        t.join(timeout)
        
        if t.is_alive():
            return "Timeout Error: Code execution took too long."
        
        if not result_queue.empty():
            return result_queue.get()
        return "No Output."