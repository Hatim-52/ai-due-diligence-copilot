import os
import sys
from pathlib import Path

# Set UTF-8 encoding for standard streams to avoid Windows charmap errors
if sys.platform == "win32":
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

ROOT_DIR = Path(__file__).resolve().parent
os.chdir(ROOT_DIR)
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# If not running with the project's venv python, delegate to it
VENV_PYTHON = ROOT_DIR / "venv" / "Scripts" / "python.exe"
if VENV_PYTHON.exists():
    current_executable = Path(sys.executable).resolve()
    target_executable = VENV_PYTHON.resolve()
    if current_executable != target_executable:
        import subprocess
        result = subprocess.run([str(target_executable), str(Path(__file__).resolve())] + sys.argv[1:])
        sys.exit(result.returncode)

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    dev_mode = os.environ.get("DEV_MODE", "").lower() in ("1", "true", "yes")
    print("=" * 60)
    print(" Due Diligence AI Copilot Server")
    print(f" Application URL: http://localhost:{port}")
    print(f" API Docs:        http://localhost:{port}/docs")
    print(f" Mode:            {'development' if dev_mode else 'production'}")
    print("=" * 60)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=dev_mode)
