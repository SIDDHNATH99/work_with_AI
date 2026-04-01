"""
Safe Python code execution via subprocess with timeout.
The child process runs with a minimal, sanitised environment.
"""

import os
import subprocess
import sys
import tempfile

_TIMEOUT_SECONDS = 15
_STDOUT_LIMIT = 5_000
_STDERR_LIMIT = 2_000

# Env vars passed through to the child process (minimal safe set)
_PASSTHROUGH_ENV = ("PATH", "PYTHONPATH", "HOME", "USERPROFILE", "TEMP", "TMP", "APPDATA")


def run_python(code: str, input_data: str = "", timeout: int = _TIMEOUT_SECONDS) -> dict:
    """
    Execute Python code in a subprocess.
    Returns dict with keys: stdout, stderr, exit_code, success.
    """
    if not code.strip():
        return {"error": "No code provided", "success": False}

    env = {k: v for k in _PASSTHROUGH_ENV if (v := os.environ.get(k))}

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            input=input_data or "",
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return {
            "stdout":    result.stdout[:_STDOUT_LIMIT],
            "stderr":    result.stderr[:_STDERR_LIMIT],
            "exit_code": result.returncode,
            "success":   result.returncode == 0,
            "truncated": len(result.stdout) > _STDOUT_LIMIT,
        }
    except subprocess.TimeoutExpired:
        return {
            "error":   f"Execution timed out after {timeout} seconds",
            "success": False,
        }
    except Exception as exc:
        return {"error": str(exc), "success": False}
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
