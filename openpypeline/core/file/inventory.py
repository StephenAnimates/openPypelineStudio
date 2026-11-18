"""Build and query filesystem paths for pipeline inventory structures.

Defines the :class:`Inventory` class for resolving hierarchical studio asset and shot directory paths and enumerating non-hidden filesystem entries.

:File: inventory.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline.core.file import inventory

    inv = inventory.Inventory(["/projects/demo", "lib", "characters", "woman", "model"])
    target_path = inv.getPath()
    items = inv.list()
"""

import os


class Inventory:
    """Build filesystem paths and list entries for a pipeline inventory.

    Resolves directory paths from an ordered list of hierarchy tokens and provides helpers for listing entries and counting files on disk.

    :ivar elements: Ordered path segments identifying the target pipeline location (for example, ``[project, module, item_type, asset, component]``).
    :vartype elements: list[str]
    """

    def __init__(self, elements: list[str]) -> None:
        """Store the ordered path elements that identify this inventory.

        :param elements: Ordered sequence of directory segments representing the pipeline hierarchy.
        """
        self.elements: list[str] = elements

    def getPath(self) -> str:
        """Construct the directory path represented by :attr:`elements`.

        When :attr:`elements` has a depth of ``5`` (indicating a component-level path), automatically inserts a ``"components"`` subdirectory after the fourth element (index ``3``).

        :returns: The joined filesystem path for the configured hierarchy.
        """
        depth = len(self.elements)
        path = ""
        count = 0

        for item in self.elements:
            if depth == 5 and count == 3:
                path = os.path.join(path, item, "components")
            else:
                path = os.path.join(path, item)
            count = count + 1

        return path

    def list(self, path: str = "") -> list[str]:
        """List non-hidden entries under the supplied or constructed path.

        Defaults to resolving the target directory via :meth:`getPath` when ``path`` is empty, and filters out dotfiles starting with ``"."``.

        :param path: Optional explicit directory path to inspect. Defaults to ``""``, which triggers :meth:`getPath`.
        :returns: List of non-hidden file and directory names inside ``path``.
        """
        if path == "":
            path = self.getPath()

        # Create list and remove hidden OS files
        inventory = [f for f in os.listdir(path) if not f.startswith(".")]
        return inventory

    def count(self) -> int:
        """Count regular files directly inside the constructed path.

        Resolves the target directory via :meth:`getPath` and counts entries for which ``os.path.isfile`` evaluates to ``True`` (excluding subdirectories).

        :returns: Number of regular files located directly inside the path.
        """
        path = self.getPath()
        file_count = len(
            [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        )
        return file_count
