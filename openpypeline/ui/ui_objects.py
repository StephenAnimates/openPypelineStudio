"""Window Manager singleton for openPypeline Studio.

Maintains references to active Qt windows and dock controls to prevent garbage collection and enable cross-component UI lookup. Replaces the legacy ``singleton.py`` implementation.

:File: ui_objects.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from typing import Any, Optional


class WindowManager:
    """Singleton window manager tracking open UI windows and dock controls.

    Prevents PySide6 widgets from being prematurely garbage-collected when created inside host applications and provides a central registry for looking up active windows.

    :ivar windows: List of active top-level window instances managed by the singleton.
    :vartype windows: list[Any]
    :ivar dock_controls: List of active host dock control wrappers managed by the singleton.
    :vartype dock_controls: list[Any]
    """

    _instance: Optional["WindowManager"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "WindowManager":
        """Return the shared window manager and initialize its registries once.

        :param args: Positional arguments forwarded to ``object.__new__``.
        :param kwargs: Keyword arguments forwarded to ``object.__new__``.
        :returns: The singleton :class:`WindowManager` instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.windows: list[Any] = []
            cls._instance.dock_controls: list[Any] = []
        return cls._instance

    def addWindow(self, window: Optional[Any] = None) -> None:
        """Keep a reference to a window so it remains alive while managed.

        :param window: Window widget instance to register if not already tracked.
        """
        if window and window not in self.windows:
            self.windows.append(window)

    def addDockControl(self, dock_ctrl: Optional[Any] = None) -> None:
        """Keep a reference to a dock control so it remains alive while managed.

        :param dock_ctrl: Host dock control instance to register if not already tracked.
        """
        if dock_ctrl and dock_ctrl not in self.dock_controls:
            self.dock_controls.append(dock_ctrl)

    def close_all(self) -> None:
        """Close all tracked windows."""
        pass  # Future enhancement hook


#: Backward-compatibility alias for :class:`WindowManager`.
UIObjects = WindowManager
