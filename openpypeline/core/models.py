"""
File: models.py
Description: Core Data Classes and Enums for openPypeline Studio.
             These models encapsulate pipeline data, replacing long argument lists
             and magic numbers throughout the framework.
"""

from dataclasses import dataclass
from enum import IntEnum

class Tab(IntEnum):
    """Represents the active browser tab in the UI."""
    ASSET = 2
    SHOT = 3

class Level(IntEnum):
    """Represents the depth level of an item in the hierarchy."""
    TYPE_OR_SEQUENCE = 1
    ASSET_OR_SHOT = 2
    COMPONENT = 3

@dataclass
class ItemContext:
    """
    Encapsulates the location of an item within the openPypeline hierarchy.
    Replaces the repetitive (tab, level1, level2, level3) arguments.
    """
    tab: int
    level1: str = ""
    level2: str = ""
    level3: str = ""

    @property
    def depth(self) -> int:
        """Returns how deep in the hierarchy this item is (0 to 3)."""
        return sum(1 for lvl in [self.level1, self.level2, self.level3] if lvl)

    @property
    def item_name(self) -> str:
        """Returns the specific name of this item."""
        if self.level3: return self.level3
        if self.level2: return self.level2
        return self.level1

    @property
    def parent_name(self) -> str:
        """Returns the name of this item's immediate parent."""
        if self.level3: return self.level2
        if self.level2: return self.level1
        return ""

@dataclass
class ProjectConfig:
    """
    Encapsulates all settings and paths for a Project.
    Replaces functions that take 22+ arguments.
    """
    name: str
    path: str
    description: str = ""
    date: str = ""
    deadline: str = ""
    status: str = "1"
    mastername: str = "master"
    masterformat: str = "ma"
    wipname: str = "wip"
    wipformat: str = "ma"
    libraryfolder: str = "scenes/assets"
    scenesfolder: str = "scenes"
    archivefolder: str = "archive"
    deletedfolder: str = "deleted"
    scriptsfolder: str = "scripts"
    rendersfolder: str = "images/renders"
    particlesfolder: str = "particles"
    texturesfolder: str = "sourceimages"
    users: str = ""
    userMode: str = "0"