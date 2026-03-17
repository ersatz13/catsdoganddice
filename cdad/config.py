import os

# Reversible scaffold switch. Keep False until the refactor path is validated.
USE_REFACTOR = False


def use_refactor_mode() -> bool:
    raw = os.getenv("CDAD_USE_REFACTOR")
    if raw is None:
        return USE_REFACTOR
    return raw.strip().lower() in {"1", "true", "yes", "on"}

