"""Run the FastAPI app while avoiding import shadowing by local modules.

This removes the empty-string entry (the current working directory)
from sys.path before importing uvicorn and the app, so standard library
modules like `platform` are resolved correctly even if a local
`platform` package exists.

Run with the repo venv Python: `venv\Scripts\python.exe run_uvicorn_no_cwd.py`
"""
import sys

if "" in sys.path:
    try:
        sys.path.remove("")
    except ValueError:
        pass

import uvicorn

def main() -> None:
    uvicorn.run("tf_wizard.app:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
