from __future__ import annotations

import os
import time
import tkinter as tk

import pytest

import app_legacy


TEST_SIZES = [
    (1280, 720),
    (1024, 768),
]


def _pump(root: tk.Tk, cycles: int = 4, delay: float = 0.0) -> None:
    for _ in range(cycles):
        root.update_idletasks()
        root.update()
        if delay:
            time.sleep(delay)


def _wait_for_assets(app: app_legacy.App, root: tk.Tk) -> None:
    for _ in range(400):
        _pump(root, cycles=1, delay=0.01)
        if app.assets_loaded:
            return
    raise AssertionError("App assets did not finish loading in time.")


def _build_app(monkeypatch: pytest.MonkeyPatch) -> tuple[app_legacy.App, tk.Tk]:
    os.environ.setdefault(
        "TCL_LIBRARY",
        "C:/Users/Bird_/AppData/Local/Programs/Python/Python310/tcl/tcl8.6",
    )
    os.environ.setdefault(
        "TK_LIBRARY",
        "C:/Users/Bird_/AppData/Local/Programs/Python/Python310/tcl/tk8.6",
    )
    for method_name in (
        "start_main_theme",
        "stop_main_theme",
        "start_shop_sound",
        "stop_shop_sound",
        "start_roll_sound",
        "stop_roll_sound",
        "start_jumble_sound",
        "stop_jumble_sound",
        "play_sound",
    ):
        monkeypatch.setattr(app_legacy.App, method_name, lambda *args, **kwargs: None)

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk UI not available in this environment: {exc}")
    root.geometry("1280x720+0+0")
    app = app_legacy.App(root)
    _wait_for_assets(app, root)
    app.skip_splash()
    _pump(root, cycles=2, delay=0.02)
    if getattr(app, "title_splash_frame", None) and app.title_splash_frame.winfo_exists():
        app.skip_title_splash()
    _pump(root, cycles=3, delay=0.02)
    return app, root


def _destroy_app(root: tk.Tk) -> None:
    try:
        root.destroy()
    except tk.TclError:
        pass


def _has_canvas_ancestor(widget: tk.Widget) -> bool:
    current = getattr(widget, "master", None)
    while current is not None:
        if isinstance(current, tk.Canvas):
            return True
        current = getattr(current, "master", None)
    return False


def _widget_path(widget: tk.Widget) -> str:
    try:
        return str(widget)
    except Exception:
        return widget.__class__.__name__


def _audit_bounds(parent: tk.Widget, issues: list[str], tolerance: int = 4) -> None:
    if not parent.winfo_exists():
        return
    try:
        parent.update_idletasks()
    except tk.TclError:
        return
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    if pw <= 1 or ph <= 1:
        return
    for child in parent.winfo_children():
        if not child.winfo_exists():
            continue
        if not child.winfo_ismapped():
            continue
        if _has_canvas_ancestor(child):
            continue
        try:
            cw = child.winfo_width()
            ch = child.winfo_height()
            cx = child.winfo_rootx()
            cy = child.winfo_rooty()
        except tk.TclError:
            continue
        if cw > 1 and ch > 1:
            if cx < px - tolerance:
                issues.append(f"{_widget_path(child)} extends left of parent {_widget_path(parent)}")
            if cy < py - tolerance:
                issues.append(f"{_widget_path(child)} extends above parent {_widget_path(parent)}")
            if cx + cw > px + pw + tolerance:
                issues.append(f"{_widget_path(child)} extends right of parent {_widget_path(parent)}")
            if cy + ch > py + ph + tolerance:
                issues.append(f"{_widget_path(child)} extends below parent {_widget_path(parent)}")
        _audit_bounds(child, issues, tolerance=tolerance)


def _assert_layout_clean(root: tk.Tk) -> None:
    _pump(root, cycles=3, delay=0.03)
    issues: list[str] = []
    _audit_bounds(root, issues)
    assert not issues, "Layout overflow detected:\n" + "\n".join(issues[:25])


def _resize(root: tk.Tk, app: app_legacy.App, width: int, height: int) -> None:
    root.geometry(f"{width}x{height}+0+0")
    _pump(root, cycles=2, delay=0.03)
    app.refresh_responsive_layout()
    _pump(root, cycles=3, delay=0.03)


def _build_setup_screen(app: app_legacy.App, root: tk.Tk) -> None:
    _pump(root, cycles=2, delay=0.02)


def _build_options_screen(app: app_legacy.App, root: tk.Tk) -> None:
    app.open_options_screen()
    _pump(root, cycles=2, delay=0.02)


def _build_naming_screen(app: app_legacy.App, root: tk.Tk) -> None:
    app.open_naming_screen()
    _pump(root, cycles=2, delay=0.02)


def _build_first_roll_screen(app: app_legacy.App, root: tk.Tk) -> None:
    app.open_naming_screen()
    _pump(root, cycles=2, delay=0.02)
    app.start_game()
    _pump(root, cycles=2, delay=0.02)


def _build_roll_phase(app: app_legacy.App, root: tk.Tk) -> None:
    _build_first_roll_screen(app, root)
    app.finish_first_player_phase()
    _pump(root, cycles=3, delay=0.03)


def _build_pause_menu(app: app_legacy.App, root: tk.Tk) -> None:
    _build_roll_phase(app, root)
    app.open_pause_menu()
    _pump(root, cycles=2, delay=0.02)


def _build_shop(app: app_legacy.App, root: tk.Tk) -> None:
    _build_roll_phase(app, root)
    app.show_shop()
    _pump(root, cycles=3, delay=0.03)


SCREEN_BUILDERS = [
    pytest.param(_build_setup_screen, id="setup"),
    pytest.param(_build_options_screen, id="options"),
    pytest.param(_build_naming_screen, id="naming"),
    pytest.param(_build_first_roll_screen, id="first-roll"),
    pytest.param(_build_roll_phase, id="roll-phase"),
    pytest.param(_build_pause_menu, id="pause-menu"),
    pytest.param(_build_shop, id="shop"),
]


@pytest.mark.parametrize("screen_builder", SCREEN_BUILDERS)
def test_key_screens_fit_within_parent_bounds(
    monkeypatch: pytest.MonkeyPatch,
    screen_builder,
) -> None:
    app, root = _build_app(monkeypatch)
    try:
        screen_builder(app, root)
        for width, height in TEST_SIZES:
            _resize(root, app, width, height)
            _assert_layout_clean(root)
    finally:
        _destroy_app(root)
