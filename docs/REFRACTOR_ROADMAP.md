# Refactor Roadmap (Reversible)

## Current Scaffold
- `app.py` is now a launcher.
- `app_legacy.py` is a full rollback snapshot.
- Mode switch:
  - `cdad/config.py` -> `USE_REFACTOR`
  - env override: `CDAD_USE_REFACTOR=1` or `0`

## Rollback
1. Set `USE_REFACTOR = False` in `cdad/config.py`, or run with `CDAD_USE_REFACTOR=0`.
2. If needed, point builds directly to `app_legacy.py`.

## Completed Segmentation
- `cdad/platform/dpi.py` -> DPI bootstrap.
- `cdad/ui/widgets/tooltip.py` -> Tooltip widget.
- `cdad/runners/legacy.py` -> legacy runtime startup.
- `cdad/refactor/main.py` -> refactor runtime entry scaffold.

## Next Safe Steps
1. Extract asset loading helpers into `cdad/services/assets.py`.
2. Extract audio helpers into `cdad/services/audio.py`.
3. Extract profile persistence into `cdad/services/profiles.py`.
4. Move one screen at a time into `cdad/ui/screens/`.
5. Keep `app_legacy.py` untouched until all screens are moved and validated.

