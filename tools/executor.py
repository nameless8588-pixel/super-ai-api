import subprocess
import sys
import os
import tempfile

def run_code(code: str, timeout: int = 10):
    try:
        # Newlines fix karo
        code = code.replace("\\n", "\n").replace("\\t", "\t")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name

        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        os.unlink(temp_file)

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "Timeout - code 10 sec se zyada chala!"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}