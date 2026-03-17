"""
Refactor runner scaffold.

Current behavior is intentionally delegated to legacy to keep rollback trivial.
As modules are extracted, this file becomes the refactor runtime root.
"""

from app_legacy import App
from cdad.runners.legacy import run

