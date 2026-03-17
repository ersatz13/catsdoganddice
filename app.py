"""
Reversible runtime launcher.

Rollback:
- Set `USE_REFACTOR = False` in `cdad/config.py`, or
- set env var `CDAD_USE_REFACTOR=0`.
"""

from cdad.config import use_refactor_mode

if use_refactor_mode():
    from cdad.refactor.main import App, run
else:
    from cdad.runners.legacy import App, run


if __name__ == "__main__":
    run()

