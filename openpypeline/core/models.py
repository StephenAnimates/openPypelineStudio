"""Core data classes and enums for openPypeline Studio.

Encapsulates pipeline hierarchy coordinates, browser tab identifiers, and project configuration settings into structured models to replace long argument lists and magic numbers throughout the framework.

:File: models.py
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline.core.models import ItemContext, Level, ProjectConfig, Tab

    ctx = ItemContext(tab=Tab.ASSET, level1="characters", level2="woman", level3="model")
    proj = ProjectConfig(name="DemoProject", path="/projects/demo")
"""

from dataclasses import dataclass
from enum import IntEnum


class Tab(IntEnum):
    """Represents the active browser tab in the UI."""

    #: Asset library browser tab (``2``).
    ASSET = 2
    #: Shot production browser tab (``3``).
    SHOT = 3


class Level(IntEnum):
    """Represents the depth level of an item in the hierarchy."""

    #: Top-level category (asset type or shot sequence) (``1``).
    TYPE_OR_SEQUENCE = 1
    #: Mid-level entity (asset or shot name) (``2``).
    ASSET_OR_SHOT = 2
    #: Leaf-level entity (asset component or shot department) (``3``).
    COMPONENT = 3


@dataclass
class ItemContext:
    """Encapsulate the location of an item within the openPypeline hierarchy.

    Replaces repetitive ``(tab, level1, level2, level3)`` argument tuples across engine, UI, and file management modules.
    """

    #: Active browser tab identifier (see :class:`Tab`).
    tab: int
    #: Top-level hierarchy token (asset type or sequence name).
    level1: str = ""
    #: Second-level hierarchy token (asset or shot name).
    level2: str = ""
    #: Third-level hierarchy token (component or department name).
    level3: str = ""

    @property
    def depth(self) -> int:
        """Return the populated hierarchy depth of this item (``0`` to ``3``).

        :returns: Count of non-empty hierarchy levels among :attr:`level1`,
            :attr:`level2`, and :attr:`level3`.
        """
        return sum(1 for lvl in [self.level1, self.level2, self.level3] if lvl)

    @property
    def item_name(self) -> str:
        """Return the specific name of the deepest populated hierarchy item.

        :returns: :attr:`level3` if set, otherwise :attr:`level2`, falling back
            to :attr:`level1`.
        """
        if self.level3:
            return self.level3
        if self.level2:
            return self.level2
        return self.level1

    @property
    def parent_name(self) -> str:
        """Return the name of this item's immediate parent in the hierarchy.

        :returns: :attr:`level2` when :attr:`level3` is set, :attr:`level1`
            when :attr:`level2` is set, or ``""`` at depth ``1`` or ``0``.
        """
        if self.level3:
            return self.level2
        if self.level2:
            return self.level1
        return ""


@dataclass
class ProjectConfig:
    """Encapsulate all settings and folder paths for an openPypeline project.

    Replaces legacy functions that required 20+ positional project arguments
    and mirrors the schema stored in ``openpypeline_projects.json``.
    """

    #: Display name of the project.
    name: str
    #: Root directory path of the project on disk.
    path: str
    #: Optional human-readable project description.
    description: str = ""
    #: Project creation date string.
    date: str = ""
    #: Target project completion or delivery deadline string.
    deadline: str = ""
    #: Project status flag (``"1"`` for active, ``"0"`` for inactive/archived).
    status: str = "1"
    #: Token used in published master filenames (defaults to ``"master"``).
    mastername: str = "master"
    #: File extension used for published master files (defaults to ``"ma"``).
    masterformat: str = "ma"
    #: Token and subdirectory name used for work-in-progress files (defaults to ``"wip"``).
    wipname: str = "wip"
    #: File extension used for work-in-progress files (defaults to ``"ma"``).
    wipformat: str = "ma"
    #: Relative path to the asset library folder (defaults to ``"scenes/assets"``).
    libraryfolder: str = "scenes/assets"
    #: Relative path to the shots/scenes folder (defaults to ``"scenes"``).
    scenesfolder: str = "scenes"
    #: Relative path to the project archive folder (defaults to ``"archive"``).
    archivefolder: str = "archive"
    #: Relative path to the soft-deleted items folder (defaults to ``"deleted"``).
    deletedfolder: str = "deleted"
    #: Relative path to project-specific scripts (defaults to ``"scripts"``).
    scriptsfolder: str = "scripts"
    #: Relative path to rendered output images (defaults to ``"images/renders"``).
    rendersfolder: str = "images/renders"
    #: Relative path to simulation and particle caches (defaults to ``"particles"``).
    particlesfolder: str = "particles"
    #: Relative path to texture and source image files (defaults to ``"sourceimages"``).
    texturesfolder: str = "sourceimages"
    #: Serialized list or string of authorized project users.
    users: str = ""
    #: User permission mode flag (defaults to ``"0"``).
    userMode: str = "0"
