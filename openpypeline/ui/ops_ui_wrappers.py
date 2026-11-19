"""UI action wrappers for openPypeline Studio.

Connects PySide6 UI button commands and signals to the core
:mod:`~openpypeline.core.ops_actions` and :mod:`~openpypeline.core.ops_info`
logic, replacing the legacy wrapper dialogs from ``openPipelineUI.mel``.

:File: ops_ui_wrappers.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
:Status: Fully migrated to PySide6. UI components are native Qt widgets.
"""

import os
from typing import Any, Optional
import webbrowser

from PySide6 import QtCore, QtGui, QtWidgets

from openpypeline.core import ops_actions as opsActions
from openpypeline.core import ops_info as opsInfo
from openpypeline.core.models import ItemContext, Level, Tab
from openpypeline.core.util import prefs

from . import ui_objects as UIObjects


def _get_resource(folder: str, filename: str) -> str:
    """Resolve the absolute POSIX path to an asset inside ``resources/``.

    Traverses three directory levels up from ``app/maya/core/`` to the
    ``openpypeline/resources/`` directory.

    :param folder: Subfolder name inside ``resources/`` (for example,
        ``"icons"`` or ``"images"``).
    :param filename: Target asset filename inside ``folder``.
    :returns: Normalized forward-slash absolute path to the resource file.
    """
    base_dir = os.path.dirname(__file__)
    # Go up 3 directories (core -> maya -> app -> openpypeline) and into 'resources'
    return os.path.abspath(
        os.path.join(base_dir, "..", "resources", folder, filename)
    ).replace("\\", "/")


def _get_ui() -> Optional[QtWidgets.QWidget]:
    """Return the live main UI window instance, or ``None`` if unavailable.

    Queries the :class:`~openpypeline.maya.ui.ui_objects.UIObjects` singleton and verifies that the underlying C++ ``QWidget`` has not been deleted.

    :returns: Live main window widget instance, or ``None`` if closed or
        uninitialized.
    """
    ui_obj = UIObjects.UIObjects()
    ui = ui_obj.opsMainUI if hasattr(ui_obj, "opsMainUI") else None
    if ui:
        try:
            ui.objectName()  # Check if C++ object is alive
        except RuntimeError:
            return None
    return ui


def refresh_ui(*args: Any) -> None:
    """Invoke UI update helpers to reflect the latest scene and project state.

    Calls :func:`update_currently_open`, :func:`update_asset_type_list`, and
    :func:`update_sequence_list`.

    :param args: Optional variadic arguments passed by Qt signals or host
        callbacks (ignored).
    """
    try:
        update_currently_open()
        update_asset_type_list()
        update_sequence_list()
    except Exception as e:
        print(f"UI Refresh warning: {e}")


def remove_secondary_windows(*args: Any) -> None:
    """Close the main window's active secondary dialog, if one is open.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if ui and hasattr(ui, "active_dialog") and ui.active_dialog:
        ui.active_dialog.close()


def close_ui(*args: Any) -> None:
    """Close the managed main window when it is available.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if ui:
        ui.close()
# --- Primary UI Updaters ---


def update_currently_open(*args: Any) -> None:
    """Refresh the currently-open item panel from preferences and file state.

    Reads active session preferences (``ops_currOpenType``,
    ``ops_currOpenCategory``, ``ops_currOpenVersion``, and hierarchy level
    keys), updates preview thumbnails, notes, event history, status badges,
    and action button states, or closes the active file via
    :func:`~openpypeline.core.ops_actions.close_file` if its directory no
    longer exists on disk.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return

    curr_type = prefs.get_pref("ops_currOpenType", "")
    curr_cat = prefs.get_pref("ops_currOpenCategory", "")
    curr_version = prefs.get_pref("ops_currOpenVersion", 0)
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")
    tab = prefs.get_pref("ops_currOpenTab", 0)

    curr_path = opsInfo.get_file_name(tab, level1, level2, level3, "folder")
    default_preview = _get_resource("images", "ops_default_preview.png")
    no_preview = _get_resource("images", "ops_no_preview.png")

    if not level1:
        clear_current_history()
        ui.ops_currOpen_scrollField.setPlainText("")
        ui.ops_currOpenPreview_img.setPixmap(QtGui.QPixmap(default_preview))

        for btn in [
            ui.ops_currOpenSaveWorkshop_btn,
            ui.ops_currOpenRecordPlayblast_btn,
            ui.ops_currOpenViewPlayblast_btn,
            ui.ops_currOpenMaster_btn,
            ui.ops_currOpenRevive_btn,
            ui.ops_currOpenClose_btn,
            ui.ops_currOpenClearNote_btn,
            ui.ops_currOpenSaveNote_btn,
            ui.ops_currOpenSnapshot_btn,
            ui.ops_currOpenExplore_btn,
        ]:
            btn.setEnabled(False)

        ui.ops_currOpenLocation_txtField.setText("")
        ui.ops_currOpenHeading_txt.setText("none")
        ui.ops_currOpenHeadingVersion_txt.setText("      ")
        ui.ops_currOpenHeadingVersion_txt.setStyleSheet(
            "font-weight: bold; background-color: #cccccc;"
        )

    elif os.path.isdir(curr_path):
        w_name = prefs.get_pref("ops_wip", "workshop")
        m_name = prefs.get_pref("ops_masterName", "master")

        num_versions = opsInfo.get_num_wips(tab, level1, level2, level3)
        latest_version = opsInfo.get_latest_wip_version(tab, level1, level2, level3)
        revive_enabled = True if num_versions > 1 else False

        version_string = (
            f"{w_name} version {curr_version}" if curr_type == "workshop" else m_name
        )
        display_string = (
            f"{level1}: {level2}  ({curr_cat.capitalize()})"
            if curr_cat in ["asset", "shot"]
            else f"{level1}: {level2}: {level3}  (Component)"
            if curr_cat in ["component", "shotComponent"]
            else ""
        )

        prev_img = opsInfo.get_thumbnail(tab, level1, level2, level3)
        ui.ops_currOpenPreview_img.setPixmap(
            QtGui.QPixmap(prev_img if os.path.isfile(prev_img) else no_preview)
        )

        note_text = opsInfo.get_custom_notes(tab, level1, level2, level3)
        ui.ops_currOpen_scrollField.setReadOnly(False)
        ui.ops_currOpen_scrollField.setPlainText(note_text)

        # Enable save button when notes are edited
        try:
            ui.ops_currOpen_scrollField.textChanged.disconnect()
        except Exception:
            pass
        ui.ops_currOpen_scrollField.textChanged.connect(
            lambda: ui.ops_currOpenSaveNote_btn.setEnabled(True)
        )

        load_current_history()

        ui.ops_currOpenRevive_btn.setEnabled(revive_enabled)
        ui.ops_currOpenRecordPlayblast_btn.setEnabled(True)
        ui.ops_currOpenViewPlayblast_btn.setEnabled(
            opsInfo.has_playblast(tab, level1, level2, level3)
        )

        for btn in [
            ui.ops_currOpenClose_btn,
            ui.ops_currOpenSaveWorkshop_btn,
            ui.ops_currOpenMaster_btn,
            ui.ops_currOpenClearNote_btn,
            ui.ops_currOpenSnapshot_btn,
            ui.ops_currOpenExplore_btn,
        ]:
            btn.setEnabled(True)

        ui.ops_currOpenSaveNote_btn.setEnabled(False)
        ui.ops_currOpenLocation_txtField.setText(curr_path)

        bgc = "#cc9980" if latest_version == curr_version else "#80b3b3"
        if curr_type == "master":
            bgc = "#e6b366"

        ui.ops_currOpenHeadingVersion_txt.setStyleSheet(
            f"font-weight: bold; background-color: {bgc}; color: black;"
        )
        ui.ops_currOpenHeadingVersion_txt.setText(version_string)
        ui.ops_currOpenHeading_txt.setText(display_string)

        if curr_type == "master":
            ui.ops_currOpenSaveWorkshop_btn.setEnabled(False)
            ui.ops_currOpenMaster_btn.setEnabled(False)
    else:
        opsActions.close_file()
        remove_secondary_windows()


def update_working_tab(index: int = 0, *args: Any) -> None:
    """Store the selected tab index and refresh the corresponding inventory panel.

    Persists ``ops_currTab`` (1-based) and triggers :func:`update_asset_type_list`
    (``index == 0``), :func:`update_sequence_list` (``index == 1``), or
    :func:`update_currently_open` (``index == 2``).

    :param index: Zero-based index of the newly selected tab widget page.
    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    prefs.set_pref("ops_currTab", index + 1)
    if index == 2:
        update_currently_open()
    elif index == 0:
        update_asset_type_list()
    elif index == 1:
        update_sequence_list()
# --- Asset Inventory Updaters ---


def update_asset_type_list(*args: Any) -> None:
    """Reload asset types, restore the current selection, and update assets.

    Queries asset-type directories via
    :func:`~openpypeline.core.ops_info.get_children`, updates
    ``ops_assetTypes`` in user preferences, restores the active selection in
    ``ops_assetType_txtScrollList``, and calls :func:`update_asset_list`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    selected = opsInfo.get_currently_selected_item(Tab.ASSET, Level.TYPE_OR_SEQUENCE)
    ui.ops_assetType_txtScrollList.clear()
    types = sorted(opsInfo.get_children(ItemContext(Tab.ASSET)))
    prefs.set_pref("ops_assetTypes", types)
    for t in types:
        ui.ops_assetType_txtScrollList.addItem(t)
        if selected == t:
            items = ui.ops_assetType_txtScrollList.findItems(t, QtCore.Qt.MatchExactly)
            if items:
                ui.ops_assetType_txtScrollList.setCurrentItem(items)
    update_asset_list(1)


def update_asset_list(preserve_selection: Any = 1, *args: Any) -> None:
    """Populate the asset list with status indicators and optional selection restore.

    Creates styled ``QListWidgetItem`` entries indicating open, published master, or WIP status, updates ``ops_assets`` in preferences, enables or disables asset management buttons, and calls :func:`asset_selected`.

    :param preserve_selection: Flag (or Qt signal payload coercible to ``int``) indicating whether to re-select the previously active asset.
    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    if isinstance(preserve_selection, (list, tuple, str)):
        preserve_selection = (
            int(preserve_selection)
            if isinstance(preserve_selection, (list, tuple))
            else int(preserve_selection)
        )
    selected = opsInfo.get_currently_selected_item(Tab.ASSET, Level.ASSET_OR_SHOT)

    ui.ops_asset_scrollList.clear()
    active = False
    assets_list = []
    master_icon = QtGui.QIcon(_get_resource("icons", "ops_icon_master.png"))
    wip_icon = QtGui.QIcon(_get_resource("icons", "ops_icon_wip.png"))

    if selected:
        assets = sorted(opsInfo.get_children(ItemContext(Tab.ASSET, selected)))
        for asset in assets:
            active = True
            assets_list.append(asset)

            item = QtWidgets.QListWidgetItem(asset)
            context = ItemContext(Tab.ASSET, selected, asset)
            is_open = (
                opsInfo.get_file_name(context, "folder")
                == opsInfo.get_currently_open_path()
            )
            has_master = opsInfo.has_master(context)
            has_wip = opsInfo.has_wip(context)

            if is_open:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setToolTip("Currently Open")

            if has_master:
                item.setIcon(master_icon)
                item.setForeground(QtGui.QColor("#e6b366"))
                if not is_open:
                    item.setToolTip("Has Published Master")
            elif has_wip:
                item.setIcon(wip_icon)
                item.setForeground(QtGui.QColor("#cc9980"))
                if not is_open:
                    item.setToolTip("Has WIP")
            else:
                item.setForeground(QtGui.QColor("#888888"))
                if not is_open:
                    item.setToolTip("Empty")

            ui.ops_asset_scrollList.addItem(item)
            if preserve_selection and selected == asset:
                ui.ops_asset_scrollList.setCurrentItem(item)

    prefs.set_pref("ops_assets", assets_list)
    ui.ops_assetTypeRemove_btn.setEnabled(bool(selected))
    ui.ops_assetNew_btn.setEnabled(bool(selected))
    ui.ops_asset_scrollList.setEnabled(active)
    asset_selected(1)


def asset_selected(preserve_selection: Any = 1, *args: Any) -> None:
    """Populate components for the selected asset and update related controls.

    Populates ``ops_componentScrollList`` with status icons and colors for each component under the selected asset, persists ``ops_components`` in preferences, updates action button enabled states, and calls
    :func:`component_selected`.

    :param preserve_selection: Flag (or Qt signal payload coercible to ``int``) indicating whether to re-select the previously active component.
    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    if isinstance(preserve_selection, (list, tuple, str)):
        preserve_selection = (
            int(preserve_selection)
            if isinstance(preserve_selection, (list, tuple))
            else int(preserve_selection)
        )
    selected = opsInfo.get_currently_selected_item(Tab.ASSET, Level.COMPONENT)

    ui.ops_componentScrollList.clear()
    is_selected = bool(selected)

    for btn in [
        ui.ops_assetRename_btn,
        ui.ops_assetRemove_btn,
        ui.ops_assetViewPlayblastAssetButton,
        ui.ops_componentNewButton,
    ]:
        btn.setEnabled(is_selected)

    active = False
    comp_list = []
    master_icon = QtGui.QIcon(_get_resource("icons", "ops_icon_master.png"))
    wip_icon = QtGui.QIcon(_get_resource("icons", "ops_icon_wip.png"))

    if is_selected:
        components = sorted(
            opsInfo.get_children(ItemContext(Tab.ASSET, selected, selected))
        )
        for comp in components:
            active = True
            comp_list.append(comp)

            item = QtWidgets.QListWidgetItem(comp)
            context = ItemContext(Tab.ASSET, selected, selected, comp)
            is_open = (
                opsInfo.get_file_name(context, "folder")
                == opsInfo.get_currently_open_path()
            )
            has_master = opsInfo.has_master(context)
            has_wip = opsInfo.has_wip(context)

            if is_open:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setToolTip("Currently Open")

            if has_master:
                item.setIcon(master_icon)
                item.setForeground(QtGui.QColor("#e6b366"))
                if not is_open:
                    item.setToolTip("Has Published Master")
            elif has_wip:
                item.setIcon(wip_icon)
                item.setForeground(QtGui.QColor("#cc9980"))
                if not is_open:
                    item.setToolTip("Has WIP")
            else:
                item.setForeground(QtGui.QColor("#888888"))
                if not is_open:
                    item.setToolTip("Empty")

            ui.ops_componentScrollList.addItem(item)
            if preserve_selection and selected == comp:
                ui.ops_componentScrollList.setCurrentItem(item)

    prefs.set_pref("ops_components", comp_list)
    ui.ops_componentScrollList.setEnabled(active)
    component_selected()


def component_selected(*args: Any) -> None:
    """Update component controls, asset details, and asset history.

    Enables or disables ``ops_componentRemoveButton`` based on the active component selection and triggers :func:`asset_information` and :func:`load_asset_history`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    selected = opsInfo.get_currently_selected_item(Tab.ASSET, Level.COMPONENT)
    is_selected = bool(selected)
    ui.ops_componentRemoveButton.setEnabled(is_selected)
    asset_information()
    load_asset_history()
# --- Shot Inventory Updaters ---


def update_sequence_list(*args: Any) -> None:
    """Reload sequences, restore the current selection, and update shots.

    Queries sequence directories via
    :func:`~openpypeline.core.ops_info.get_children`, updates
    ``ops_sequences`` in user preferences, restores the active selection in
    ``ops_sequenceScrollList``, and calls :func:`update_shot_list`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    selected = opsInfo.get_currently_selected_item(Tab.SHOT, Level.TYPE_OR_SEQUENCE)
    ui.ops_sequenceScrollList.clear()
    seqs = sorted(opsInfo.get_children(ItemContext(Tab.SHOT)))
    prefs.set_pref("ops_sequences", seqs)
    for seq in seqs:
        ui.ops_sequenceScrollList.addItem(seq)
        if selected == seq:
            items = ui.ops_sequenceScrollList.findItems(seq, QtCore.Qt.MatchExactly)
            if items:
                ui.ops_sequenceScrollList.setCurrentItem(items)
    update_shot_list(1)


def update_shot_list(preserve_selection: Any = 1, *args: Any) -> None:
    """Populate the shot list with status indicators and optional selection restore.

    Creates styled ``QListWidgetItem`` entries indicating open, published master, or WIP status, updates ``ops_shots`` in preferences, enables or disables shot management buttons, and calls :func:`shot_selected`.

    :param preserve_selection: Flag (or Qt signal payload coercible to ``int``) indicating whether to re-select the previously active shot.
    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    if isinstance(preserve_selection, (list, tuple, str)):
        preserve_selection = (
            int(preserve_selection)
            if isinstance(preserve_selection, (list, tuple))
            else int(preserve_selection)
        )
    selected = opsInfo.get_currently_selected_item(Tab.SHOT, Level.ASSET_OR_SHOT)
    ui.ops_shotScrollList.clear()
    active = False
    shots_list = []
    master_icon = QtGui.QIcon(_get_resource("icons", "ops_icon_master.png"))
    wip_icon = QtGui.QIcon(_get_resource("icons", "ops_icon_wip.png"))

    if selected:
        shots = sorted(opsInfo.get_children(ItemContext(Tab.SHOT, selected)))
        for shot in shots:
            active = True
            shots_list.append(shot)

            item = QtWidgets.QListWidgetItem(shot)
            context = ItemContext(Tab.SHOT, selected, shot)
            is_open = (
                opsInfo.get_file_name(context, "folder")
                == opsInfo.get_currently_open_path()
            )
            has_master = opsInfo.has_master(context)
            has_wip = opsInfo.has_wip(context)

            if is_open:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setToolTip("Currently Open")

            if has_master:
                item.setIcon(master_icon)
                item.setForeground(QtGui.QColor("#e6b366"))
                if not is_open:
                    item.setToolTip("Has Published Master")
            elif has_wip:
                item.setIcon(wip_icon)
                item.setForeground(QtGui.QColor("#cc9980"))
                if not is_open:
                    item.setToolTip("Has WIP")
            else:
                item.setForeground(QtGui.QColor("#888888"))
                if not is_open:
                    item.setToolTip("Empty")

            ui.ops_shotScrollList.addItem(item)
            if preserve_selection and selected == shot:
                ui.ops_shotScrollList.setCurrentItem(item)

    prefs.set_pref("ops_shots", shots_list)
    ui.ops_sequenceRemoveButton.setEnabled(bool(selected))
    ui.ops_shotNewButton.setEnabled(bool(selected))
    ui.ops_shotScrollList.setEnabled(active)
    shot_selected(1)


def shot_selected(preserve_selection: Any = 1, *args: Any) -> None:
    """Populate components for the selected shot and update related controls.

    Populates ``ops_shotComponentScrollList`` with status icons and colors for each component under the selected shot, persists ``ops_shotComponents`` in preferences, updates action button enabled states, and calls :func:`shot_component_selected`.

    :param preserve_selection: Flag (or Qt signal payload coercible to ``int``) indicating whether to re-select the previously active shot component.
    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    if isinstance(preserve_selection, (list, tuple, str)):
        preserve_selection = (
            int(preserve_selection)
            if isinstance(preserve_selection, (list, tuple))
            else int(preserve_selection)
        )
    selected = opsInfo.get_currently_selected_item(Tab.SHOT, Level.COMPONENT)
    ui.ops_shotComponentScrollList.clear()
    is_selected = bool(selected)

    for btn in [
        ui.ops_shotRemoveButton,
        ui.ops_shotComponentNewButton,
        ui.ops_shotViewPlayblastButton,
    ]:
        btn.setEnabled(is_selected)

    active = False
    s_comp_list = []
    master_icon = QtGui.QIcon(_get_resource("icons", "ops_icon_master.png"))
    wip_icon = QtGui.QIcon(_get_resource("icons", "ops_icon_wip.png"))

    if is_selected:
        components = sorted(
            opsInfo.get_children(ItemContext(Tab.SHOT, selected, selected))
        )
        for comp in components:
            active = True
            s_comp_list.append(comp)

            item = QtWidgets.QListWidgetItem(comp)
            context = ItemContext(Tab.SHOT, selected, selected, comp)
            is_open = (
                opsInfo.get_file_name(context, "folder")
                == opsInfo.get_currently_open_path()
            )
            has_master = opsInfo.has_master(context)
            has_wip = opsInfo.has_wip(context)

            if is_open:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setToolTip("Currently Open")

            if has_master:
                item.setIcon(master_icon)
                item.setForeground(QtGui.QColor("#e6b366"))
                if not is_open:
                    item.setToolTip("Has Published Master")
            elif has_wip:
                item.setIcon(wip_icon)
                item.setForeground(QtGui.QColor("#cc9980"))
                if not is_open:
                    item.setToolTip("Has WIP")
            else:
                item.setForeground(QtGui.QColor("#888888"))
                if not is_open:
                    item.setToolTip("Empty")

            ui.ops_shotComponentScrollList.addItem(item)
            if preserve_selection and selected == comp:
                ui.ops_shotComponentScrollList.setCurrentItem(item)

    prefs.set_pref("ops_shotComponents", s_comp_list)
    ui.ops_shotComponentScrollList.setEnabled(active)
    shot_component_selected()


def shot_component_selected(*args: Any) -> None:
    """Update shot-component controls, details, and history for the selection.

    Enables or disables ``ops_shotComponentRemoveButton`` based on the active shot component selection and triggers :func:`shot_information` and
    :func:`load_shot_history`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    selected = opsInfo.get_currently_selected_item(Tab.SHOT, Level.COMPONENT)
    is_selected = bool(selected)
    ui.ops_shotComponentRemoveButton.setEnabled(is_selected)
    shot_information()
    load_shot_history()
# --- Information and History Blocks ---


def asset_information(*args: Any) -> None:
    """Display the selected asset's folder, notes, and preview image.

    Resolves the active :class:`~openpypeline.core.models.ItemContext` under
    ``Tab.ASSET``, loads its thumbnail (falling back to
    ``ops_no_preview.png`` or ``ops_default_preview.png``), populates
    ``ops_assetLocationField`` and ``ops_assetNoteField``, and toggles
    ``ops_assetViewPlayblastAssetButton``.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    selected = opsInfo.get_currently_selected_item(Tab.ASSET, Level.COMPONENT)
    context = ItemContext(Tab.ASSET, selected, selected, selected)
    preview_file = _get_resource("images", "ops_default_preview.png")
    output_text = ""

    if selected:
        thumb = opsInfo.get_thumbnail(context)
        if os.path.isfile(thumb):
            preview_file = thumb
        else:
            preview_file = _get_resource("images", "ops_no_preview.png")
        output_text = opsInfo.get_custom_notes(context)
        ui.ops_assetViewPlayblastAssetButton.setEnabled(opsInfo.has_playblast(context))
    else:
        ui.ops_assetViewPlayblastAssetButton.setEnabled(False)

    folder = opsInfo.get_file_name(context, "folder")
    ui.ops_assetLocationField.setText(folder)
    ui.ops_assetNoteField.setPlainText(output_text)
    ui.ops_assetPreviewImage.setPixmap(QtGui.QPixmap(preview_file))


def shot_information(*args: Any) -> None:
    """Display the selected shot's folder, notes, preview, and playblast state.

    Resolves the active :class:`~openpypeline.core.models.ItemContext` under
    ``Tab.SHOT``, loads its thumbnail (falling back to
    ``ops_no_preview.png`` or ``ops_default_preview.png``), populates
    ``ops_shotLocationField`` and ``ops_shotInfoField``, and toggles
    ``ops_shotViewPlayblastButton``.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    selected = opsInfo.get_currently_selected_item(Tab.SHOT, Level.COMPONENT)
    context = ItemContext(Tab.SHOT, selected, selected, selected)
    preview_file = _get_resource("images", "ops_default_preview.png")
    output_text = ""

    if selected:
        thumb = opsInfo.get_thumbnail(context)
        if os.path.isfile(thumb):
            preview_file = thumb
        else:
            preview_file = _get_resource("images", "ops_no_preview.png")
        output_text = opsInfo.get_custom_notes(context)
        ui.ops_shotViewPlayblastButton.setEnabled(opsInfo.has_playblast(context))
    else:
        ui.ops_shotViewPlayblastButton.setEnabled(False)

    folder = opsInfo.get_file_name(context, "folder")
    ui.ops_shotLocationField.setText(folder)
    ui.ops_shotInfoField.setPlainText(output_text)
    ui.ops_shotPreviewImage.setPixmap(QtGui.QPixmap(preview_file))


def load_asset_history(*args: Any) -> None:
    """Display event notes for the currently selected asset component.

    Reads the event log via :func:`~openpypeline.core.ops_info.get_event_notes` and writes it into ``ops_commentField``.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    selected = opsInfo.get_currently_selected_item(Tab.ASSET, Level.COMPONENT)
    context = ItemContext(Tab.ASSET, selected, selected, selected)
    history_text = opsInfo.get_event_notes(context)
    ui.ops_commentField.setPlainText(history_text)


def load_shot_history(*args: Any) -> None:
    """Display event notes for the currently selected shot component.

    Reads the event log via :func:`~openpypeline.core.ops_info.get_event_notes` and writes it into ``ops_shotCommentField``.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    selected = opsInfo.get_currently_selected_item(Tab.SHOT, Level.COMPONENT)
    context = ItemContext(Tab.SHOT, selected, selected, selected)
    history_text = opsInfo.get_event_notes(context)
    ui.ops_shotCommentField.setPlainText(history_text)


def load_current_history(*args: Any) -> None:
    """Display event notes for the item shown in the currently-open panel.

    Reads active session preferences (``ops_currOpenTab`` and level keys) and populates ``ops_currOpenAssetNote_scrollField`` via :func:`~openpypeline.core.ops_info.get_event_notes`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    tab = prefs.get_pref("ops_currOpenTab", 0)
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")
    history_text = opsInfo.get_event_notes(tab, level1, level2, level3)
    ui.ops_currOpenAssetNote_scrollField.setPlainText(history_text)


def clear_current_history(*args: Any) -> None:
    """Clear the currently-open item's read-only history display.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    ui.ops_currOpenAssetNote_scrollField.setPlainText("")
def open_currently_selected(
    tab: int, level: int, item_type: str, version_offset: int = 0, *args: Any
) -> None:
    """Open the selected item version, switch to its tab, and refresh the UI.

    Resolves the active :class:`~openpypeline.core.models.ItemContext` via :func:`~openpypeline.core.ops_info.get_current_context`, opens the item through :func:`~openpypeline.core.ops_actions.open_item`, switches the main tab widget to the Currently Open tab (index ``2``), and calls :func:`refresh_ui`.

    :param tab: Tab index identifying the inventory domain (for example, ``Tab.ASSET`` or ``Tab.SHOT``).
    :param level: Hierarchy depth level of the selected item.
    :param item_type: Target file category to open (for example, ``"workshop"`` or ``"master"``).
    :param version_offset: Relative offset from the latest version when opening a workshop file (``0`` opens the latest version).
    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    context = opsInfo.get_current_context(tab, level)
    if opsActions.open_item(context, item_type, version_offset):
        ui = _get_ui()
        if ui:
            ui.ops_mainTabs_tabLayout.setCurrentIndex(2)
        refresh_ui()


def import_selected(tab: int, level: int, item_type: str, *args: Any) -> None:
    """Import the selected item of the requested type into the current scene.

    :param tab: Tab index identifying the inventory domain.
    :param level: Hierarchy depth level of the selected item.
    :param item_type: Target file category to import (for example, ``"workshop"`` or ``"master"``).
    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    context = opsInfo.get_current_context(tab, level)
    opsActions.import_item(context, item_type, "")


def reference_selected(tab: int, level: int, item_type: str, *args: Any) -> None:
    """Reference the selected item of the requested type into the current scene.

    :param tab: Tab index identifying the inventory domain.
    :param level: Hierarchy depth level of the selected item.
    :param item_type: Target file category to reference (for example, ``"workshop"`` or ``"master"``).
    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    context = opsInfo.get_current_context(tab, level)
    opsActions.reference_item(context, item_type, "")


def remove_process(tab: int, depth: int, *args: Any) -> None:
    """Remove the item at the selected hierarchy depth and refresh on success.

    :param tab: Tab index identifying the inventory domain.
    :param depth: Hierarchy depth level of the item to remove.
    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    context = opsInfo.get_current_context(tab, depth)
    if opsActions.remove_item(context):
        refresh_ui()


def explore_selected(tab: int, *args: Any) -> None:
    """Open the filesystem location for the selected inventory item.

    :param tab: Tab index identifying the inventory domain.
    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    context = opsInfo.get_current_context(tab, 3)
    opsActions.open_location(context)


def explore_current(*args: Any) -> None:
    """Open the filesystem location for the currently-open item.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    tab = prefs.get_pref("ops_currOpenTab", 0)
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")
    context = ItemContext(tab, level1, level2, level3)
    opsActions.open_location(context)


def view_playblast_selected(tab: int, *args: Any) -> None:
    """Open the playblast associated with the selected inventory item.

    :param tab: Tab index identifying the inventory domain.
    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    context = opsInfo.get_current_context(tab, 3)
    opsActions.view_playblast(context)


def view_playblast_current(*args: Any) -> None:
    """Open the playblast associated with the currently-open item.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    tab = prefs.get_pref("ops_currOpenTab", 0)
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")
    context = ItemContext(tab, level1, level2, level3)
    opsActions.view_playblast(context)


def record_current_playblast(*args: Any) -> None:
    """Record a playblast for the current item and refresh the UI.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    tab = prefs.get_pref("ops_currOpenTab", 0)
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")
    context = ItemContext(tab, level1, level2, level3)
    opsActions.record_playblast(context)
    refresh_ui()


def take_snapshot(*args: Any) -> None:
    """Create and display a thumbnail for the currently-open item.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    tab = prefs.get_pref("ops_currOpenTab", 0)
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")
    context = ItemContext(tab, level1, level2, level3)
    img = opsActions.create_thumbnail(context)
    if os.path.isfile(img):
        ui = _get_ui()
        if ui:
            ui.ops_currOpenPreview_img.setPixmap(QtGui.QPixmap(img))


def save_note(*args: Any) -> None:
    """Save the currently-open item's edited custom notes.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not ui:
        return
    tab = prefs.get_pref("ops_currOpenTab", 0)
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")
    context = ItemContext(tab, level1, level2, level3)
    text = ui.ops_currOpen_scrollField.toPlainText()
    opsActions.set_custom_notes(context, text)
    ui.ops_currOpenSaveNote_btn.setEnabled(False)


def clear_note(*args: Any) -> None:
    """Clear and save the custom notes for the currently-open item.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if ui:
        ui.ops_currOpen_scrollField.setPlainText("")
        save_note()


def close_current(*args: Any) -> None:
    """Close the active scene file and refresh the UI when successful.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    if opsActions.close_file():
        refresh_ui()


def launch_help(*args: Any) -> None:
    """Open the bundled help page or the project's online documentation.

    Checks for a local Sphinx build at ``docs/_build/html/index.html`` and opens it in the default web browser, falling back to the hosted GitHub Pages documentation URL.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    base_dir = os.path.dirname(__file__)
    docs_index = os.path.abspath(
        os.path.join(base_dir, "..", "..", "docs", "_build", "html", "index.html")
    ).replace("\\", "/")

    if os.path.exists(docs_index):
        webbrowser.open(f"file://{docs_index}")
    else:
        webbrowser.open(
            "https://stephenanimates.github.io/openPypelineStudio/index.html"
        )
# --- UI Dialog Wrappers ---


class ItemCreationDialog(QtWidgets.QDialog):
    """Modal dialog collecting a new item name and scene-creation mode.

    Presents a text input field alongside radio buttons allowing the artist to start with an empty item (mode ``1``), export the current selection (mode ``2``), or export the entire scene (mode ``3``).

    :ivar create_callback: Callable invoked with ``(mode: int, name: str)`` when the artist confirms creation.
    :vartype create_callback: Callable[[int, str], None]
    :ivar name_field: Line edit capturing the new item name.
    :vartype name_field: QtWidgets.QLineEdit
    :ivar radio_empty: Radio button selecting empty item creation (mode ``1``).
    :vartype radio_empty: QtWidgets.QRadioButton
    :ivar radio_export_sel: Radio button selecting selection export (mode ``2``).
    :vartype radio_export_sel: QtWidgets.QRadioButton
    :ivar radio_export_all: Radio button selecting full-scene export (mode ``3``).
    :vartype radio_export_all: QtWidgets.QRadioButton
    """

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget],
        title: str,
        field_label: str,
        create_callback: Any,
    ) -> None:
        """Build the name field, export-mode choices, and dialog buttons.

        :param parent: Parent widget for modal dialog centering.
        :param title: Window title displayed on the dialog frame.
        :param field_label: Descriptive prompt label placed above :attr:`name_field`.
        :param create_callback: Callback receiving ``(mode, name)`` when the **Create** button is clicked.
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.create_callback = create_callback

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel(field_label))

        self.name_field = QtWidgets.QLineEdit()
        layout.addWidget(self.name_field)

        self.radio_empty = QtWidgets.QRadioButton("Start with empty item")
        self.radio_export_sel = QtWidgets.QRadioButton("Export current selection")
        self.radio_export_all = QtWidgets.QRadioButton("Export current scene")
        self.radio_empty.setChecked(True)

        layout.addWidget(self.radio_empty)
        layout.addWidget(self.radio_export_sel)
        layout.addWidget(self.radio_export_all)

        btn_layout = QtWidgets.QHBoxLayout()
        create_btn = QtWidgets.QPushButton("Create")
        cancel_btn = QtWidgets.QPushButton("Cancel")

        create_btn.clicked.connect(self.on_create)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def on_create(self) -> None:
        """Pass the selected creation mode and trimmed name to the callback."""
        mode = 1
        if self.radio_export_sel.isChecked():
            mode = 2
        elif self.radio_export_all.isChecked():
            mode = 3
        self.create_callback(mode, self.name_field.text().strip())
        self.accept()


def prompt_new_asset_type(*args: Any) -> None:
    """Prompt for and create a new asset type in the active project.

    Displays a warning if no project is currently active; otherwise prompts for a type name, creates it via :func:`~openpypeline.core.ops_actions.create_new_item` (mode ``0``), and calls :func:`refresh_ui`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not prefs.get_pref("ops_currProjectName", ""):
        QtWidgets.QMessageBox.warning(ui, "Error", "No Project is currently active.")
        return
    name, ok = QtWidgets.QInputDialog.getText(
        ui,
        "New Asset Type",
        "Asset Type Name\n(no spaces or special characters):",
    )
    if ok and name.strip():
        context = ItemContext(Tab.ASSET, name.strip())
        if opsActions.create_new_item(context, 0):
            refresh_ui()


def prompt_new_sequence(*args: Any) -> None:
    """Prompt for and create a new shot sequence in the active project.

    Displays a warning if no project is currently active; otherwise prompts for a sequence name, creates it via :func:`~openpypeline.core.ops_actions.create_new_item` (mode ``0``), and calls :func:`refresh_ui`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    if not prefs.get_pref("ops_currProjectName", ""):
        QtWidgets.QMessageBox.warning(ui, "Error", "No Project is currently active.")
        return
    name, ok = QtWidgets.QInputDialog.getText(
        ui,
        "New Sequence",
        "Sequence Name\n(no spaces or special characters):",
    )
    if ok and name.strip():
        context = ItemContext(Tab.SHOT, name.strip())
        if opsActions.create_new_item(context, 0):
            refresh_ui()


def prompt_new_asset(*args: Any) -> None:
    """Prompt for an asset name and whether to export scene content into it.

    Opens :class:`ItemCreationDialog` under the currently selected asset type and delegates creation to
    :func:`~openpypeline.core.ops_actions.create_new_item`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    selected = opsInfo.get_currently_selected_item(Tab.ASSET, Level.TYPE_OR_SEQUENCE)
    if not selected:
        QtWidgets.QMessageBox.warning(ui, "Error", "No Asset Type selected.")
        return

    def _create(mode: int, name: str) -> None:
        """Create the asset under the selected type using the chosen mode."""
        context = ItemContext(Tab.ASSET, selected, name)
        if opsActions.create_new_item(context, mode):
            refresh_ui()

    dlg = ItemCreationDialog(
        ui,
        "Create New Asset",
        "Asset Name (no spaces or special chars):",
        _create,
    )
    ui.active_dialog = dlg
    dlg.exec()


def prompt_new_asset_component(*args: Any) -> None:
    """Prompt for and create a component under the selected asset.

    Opens :class:`ItemCreationDialog` under the currently selected asset and delegates creation to :func:`~openpypeline.core.ops_actions.create_new_item`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    selected = opsInfo.get_currently_selected_item(Tab.ASSET, Level.ASSET_OR_SHOT)
    if not selected:
        QtWidgets.QMessageBox.warning(ui, "Error", "No Asset selected.")
        return

    def _create(mode: int, name: str) -> None:
        """Create the component under the selected asset using the chosen mode."""
        context = ItemContext(Tab.ASSET, selected, selected, name)
        if opsActions.create_new_item(context, mode):
            refresh_ui()

    dlg = ItemCreationDialog(
        ui,
        "Create New Component",
        "Component Name (no spaces or special chars):",
        _create,
    )
    ui.active_dialog = dlg
    dlg.exec()


def prompt_new_shot(*args: Any) -> None:
    """Prompt for and create a shot under the selected sequence.

    Opens :class:`ItemCreationDialog` under the currently selected sequence and delegates creation to
    :func:`~openpypeline.core.ops_actions.create_new_item`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    selected = opsInfo.get_currently_selected_item(Tab.SHOT, Level.TYPE_OR_SEQUENCE)
    if not selected:
        QtWidgets.QMessageBox.warning(ui, "Error", "No Sequence selected.")
        return

    def _create(mode: int, name: str) -> None:
        """Create the shot under the selected sequence using the chosen mode."""
        context = ItemContext(Tab.SHOT, selected, name)
        if opsActions.create_new_item(context, mode):
            refresh_ui()

    dlg = ItemCreationDialog(
        ui,
        "Create New Shot",
        "Shot Name (no spaces or special chars):",
        _create,
    )
    ui.active_dialog = dlg
    dlg.exec()
def prompt_new_shot_component(*args: Any) -> None:
    """Prompt for and create a component under the selected shot.

    Opens :class:`ItemCreationDialog` under the currently selected shot and delegates creation to :func:`~openpypeline.core.ops_actions.create_new_item`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    selected = opsInfo.get_currently_selected_item(Tab.SHOT, Level.ASSET_OR_SHOT)
    if not selected[1]:
        QtWidgets.QMessageBox.warning(ui, "Error", "No Shot selected.")
        return

    def _create(mode: int, name: str) -> None:
        """Create the component under the selected shot using the chosen mode."""
        context = ItemContext(Tab.SHOT, selected[0], selected[1], name)
        if opsActions.create_new_item(context, mode):
            refresh_ui()

    dlg = ItemCreationDialog(
        ui,
        "Create New Shot Component",
        "Component Name (no spaces or special chars):",
        _create,
    )
    ui.active_dialog = dlg
    dlg.exec()


def prompt_rename_asset(*args: Any) -> None:
    """Prompt for a replacement asset name and apply the rename.

    Prompts for a new asset name, delegates renaming to
    :func:`~openpypeline.app.maya.core.rename_asset.renameAsset`, and calls
    :func:`refresh_ui`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    selected = opsInfo.get_currently_selected_item(2, 2)
    if not selected[1]:
        return
    name, ok = QtWidgets.QInputDialog.getText(
        ui,
        "Rename Asset",
        "New Asset Name (no spaces or special chars):",
    )
    if ok and name.strip():
        from openpypeline.core import rename_asset as renameAsset

        asset_path = opsInfo.get_file_name(2, selected[0], selected[1], selected[2], "folder")
        renameAsset.renameAsset(asset_path, name.strip())
        refresh_ui()


def prompt_save_wip(*args: Any) -> None:
    """Prompt for a WIP comment, save the current scene, and refresh the UI.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    w_name = prefs.get_pref("ops_wip", "WIP").upper()
    comment, ok = QtWidgets.QInputDialog.getText(ui, f"Save {w_name}", "Comment:")
    if ok:
        opsActions.save_wip(comment)
        refresh_ui()
class ReviveDialog(QtWidgets.QDialog):
    """Modal dialog letting the user choose an older WIP version to restore.

    Lists all prior WIP versions (skipping index ``0``, the current latest version) and restores the chosen version by opening it and saving it as a new incremental WIP.

    :ivar context: Hierarchy coordinates of the item being revived (see :class:`~openpypeline.core.models.ItemContext`).
    :vartype context: ItemContext
    :ivar list_widget: List widget displaying available older WIP versions.
    :vartype list_widget: QtWidgets.QListWidget
    """

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget],
        w_name: str,
        workshops: list[str],
        context: ItemContext,
    ) -> None:
        """Build a list of older WIP versions and connect the revive action.

        :param parent: Parent widget for modal dialog centering.
        :param w_name: Display label for WIP files (for example, ``"WIP"``).
        :param workshops: Ordered list of existing WIP file paths, sorted newest-first so index ``0`` is the latest version.
        :param context: Target :class:`~openpypeline.core.models.ItemContext`
            whose version history is being restored.
        """
        super().__init__(parent)
        self.setWindowTitle(f"Revive {w_name}")
        self.context = context

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(
            QtWidgets.QLabel(f"Select a previous {w_name} version to revive:")
        )

        self.list_widget = QtWidgets.QListWidget()
        # Skip index 0 (the latest version)
        for i in range(1, len(workshops)):
            version = opsInfo.get_version_from_file(workshops[i])
            item = QtWidgets.QListWidgetItem(f"Version {version:04d}")
            item.setData(QtCore.Qt.UserRole, i)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)

        btn_layout = QtWidgets.QHBoxLayout()
        revive_btn = QtWidgets.QPushButton("Revive")
        revive_btn.setStyleSheet("background-color: #80b3b3; color: black;")
        cancel_btn = QtWidgets.QPushButton("Cancel")

        revive_btn.clicked.connect(self.on_revive)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(revive_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def on_revive(self) -> None:
        """Open the selected older WIP, save it as a new version, and refresh."""
        sel = self.list_widget.selectedItems()
        if not sel:
            return
        offset = sel.data(QtCore.Qt.UserRole)
        if opsActions.open_item(self.context, "workshop", offset):
            opsActions.save_wip("Revived from an older version.")
        self.accept()
        refresh_ui()


def prompt_revive(*args: Any) -> None:
    """Open the version-revival dialog when older WIP versions are available.

    Queries the currently open item's WIP history via :func:`~openpypeline.core.ops_info.get_wips`, displays a warning if fewer than two WIP versions exist, and opens :class:`ReviveDialog`.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    tab = prefs.get_pref("ops_currOpenTab", 0)
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")

    if not level1:
        return

    w_name = prefs.get_pref("ops_wip", "WIP").upper()

    context = ItemContext(tab, level1, level2, level3)
    wips = opsInfo.get_wips(context)
    if not wips or len(wips) < 2:
        QtWidgets.QMessageBox.warning(
            ui, "Warning", f"Not enough {w_name} files to revive."
        )
        return

    dlg = ReviveDialog(ui, w_name, wips, context)
    ui.active_dialog = dlg
    dlg.exec()
class ArchiveDialog(QtWidgets.QDialog):
    """Modal dialog for archiving, retrieving, and deleting old item versions.

    Provides controls to move older WIP and master versions into the project's
    archive directory while retaining a configurable number of recent versions,
    restore archived files back to working folders, or move archived files to
    the deleted-items directory.

    :ivar context: Hierarchy coordinates of the target item (see :class:`~openpypeline.core.models.ItemContext`).
    :vartype context: ItemContext
    :ivar chk_w: Checkbox toggling WIP file archiving.
    :vartype chk_w: QtWidgets.QCheckBox
    :ivar chk_m: Checkbox toggling master version archiving.
    :vartype chk_m: QtWidgets.QCheckBox
    :ivar spin_w: Spin box specifying how many recent WIP versions to retain.
    :vartype spin_w: QtWidgets.QSpinBox
    :ivar spin_m: Spin box specifying how many recent master versions to retain.
    :vartype spin_m: QtWidgets.QSpinBox
    :ivar r_chk_w: Checkbox toggling retrieval of archived WIP files.
    :vartype r_chk_w: QtWidgets.QCheckBox
    :ivar r_chk_m: Checkbox toggling retrieval of archived master versions.
    :vartype r_chk_m: QtWidgets.QCheckBox
    """

    def __init__(
        self, parent: Optional[QtWidgets.QWidget], context: ItemContext
    ) -> None:
        """Build controls for archiving, retrieving, and deleting old versions.

        :param parent: Parent widget for modal dialog centering.
        :param context: Target :class:`~openpypeline.core.models.ItemContext`
            whose archive operations are being configured.
        """
        super().__init__(parent)
        self.context = context

        w_name = prefs.get_pref("ops_wip", "WIP").upper()
        m_name = prefs.get_pref("ops_masterName", "master").capitalize()

        item_name_str = f"{context.level1}"
        if context.level2:
            item_name_str += f": {context.level2}"
        if context.level3:
            item_name_str += f": {context.level3}"

        self.setWindowTitle(f"Archive - {item_name_str}")
        layout = QtWidgets.QVBoxLayout(self)

        # Archive Group
        grp1 = QtWidgets.QGroupBox("Archive")
        l1 = QtWidgets.QVBoxLayout(grp1)
        l1.addWidget(
            QtWidgets.QLabel(
                f"Archiving the selected item will clean up its working directory\n"
                f"by moving old {w_name} files and old {m_name} versions to the Archive\n"
                f"folder. The most recent files won't be affected."
            )
        )

        chk_layout = QtWidgets.QHBoxLayout()
        self.chk_w = QtWidgets.QCheckBox(f"Archive {w_name} Files")
        self.chk_w.setChecked(True)
        self.chk_m = QtWidgets.QCheckBox(f"Archive {m_name} Versions")
        self.chk_m.setChecked(True)
        chk_layout.addWidget(self.chk_w)
        chk_layout.addWidget(self.chk_m)
        l1.addLayout(chk_layout)

        spin_layout = QtWidgets.QHBoxLayout()
        spin_layout.addWidget(QtWidgets.QLabel("Keep most recent:"))
        self.spin_w = QtWidgets.QSpinBox()
        self.spin_w.setMinimum(1)
        spin_layout.addWidget(self.spin_w)
        spin_layout.addStretch()
        spin_layout.addWidget(QtWidgets.QLabel("Keep most recent:"))
        self.spin_m = QtWidgets.QSpinBox()
        self.spin_m.setMinimum(1)
        spin_layout.addWidget(self.spin_m)
        l1.addLayout(spin_layout)

        btn_arch = QtWidgets.QPushButton("Archive")
        btn_arch.setStyleSheet("background-color: #99b3e6;")
        btn_arch.clicked.connect(self.on_archive)
        l1.addWidget(btn_arch)
        layout.addWidget(grp1)

        # Retrieve Group
        grp2 = QtWidgets.QGroupBox("Retrieve")
        l2 = QtWidgets.QVBoxLayout(grp2)
        l2.addWidget(
            QtWidgets.QLabel(
                "Retrieving archived files for the current item will return them\n"
                "to their original working directories."
            )
        )
        r_chk_layout = QtWidgets.QHBoxLayout()
        self.r_chk_w = QtWidgets.QCheckBox(f"Retrieve {w_name} Files")
        self.r_chk_m = QtWidgets.QCheckBox(f"Retrieve {m_name} Versions")
        r_chk_layout.addWidget(self.r_chk_w)
        r_chk_layout.addWidget(self.r_chk_m)
        l2.addLayout(r_chk_layout)

        btn_ret = QtWidgets.QPushButton("Retrieve")
        btn_ret.clicked.connect(self.on_retrieve)
        l2.addWidget(btn_ret)
        layout.addWidget(grp2)

        # Delete Group
        grp3 = QtWidgets.QGroupBox("Delete")
        l3 = QtWidgets.QVBoxLayout(grp3)
        l3.addWidget(
            QtWidgets.QLabel(
                "This will move all archived files for this item to the 'deleted' folder."
            )
        )
        btn_del = QtWidgets.QPushButton("Delete Archive")
        btn_del.setStyleSheet("background-color: #ffb399;")
        btn_del.clicked.connect(self.on_delete)
        l3.addWidget(btn_del)
        layout.addWidget(grp3)

        btn_close = QtWidgets.QPushButton("Close")
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)

    def on_archive(self) -> None:
        """Archive selected WIP and master versions while retaining chosen counts."""
        w_val = self.spin_w.value() if self.chk_w.isChecked() else 0
        m_val = self.spin_m.value() if self.chk_m.isChecked() else 0
        opsActions.archive_item(self.context, w_val, m_val)
        refresh_ui()
        self.accept()

    def on_retrieve(self) -> None:
        """Retrieve the selected archived file categories and refresh the UI."""
        opsActions.retrieve_archive(
            self.context, self.r_chk_w.isChecked(), self.r_chk_m.isChecked()
        )
        refresh_ui()
        self.accept()

    def on_delete(self) -> None:
        """Move the item's archived files to the deleted-items location."""
        opsActions.remove_archive(self.context)
        self.accept()


def prompt_archive(tab: int, level: int, *args: Any) -> None:
    """Open the archive dialog for the item at the requested selection depth.

    Resolves the active :class:`~openpypeline.core.models.ItemContext` via
    :func:`~openpypeline.core.ops_info.get_current_context` and opens
    :class:`ArchiveDialog` when a valid top-level item is selected.

    :param tab: Tab index identifying the inventory domain.
    :param level: Hierarchy depth level of the selected item.
    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    ui = _get_ui()
    context = opsInfo.get_current_context(tab, level)
    if not context.level1:
        return
    dlg = ArchiveDialog(ui, context)
    ui.active_dialog = dlg
    dlg.exec()


def about_dialog(*args: Any) -> None:
    """Display the openPypeline Studio description and documentation link.

    :param args: Optional variadic arguments passed by Qt signals (ignored).
    """
    text = (
        "openPypeline Studio (ops)<br><br>"
        "An open source, free, and customizable python pipeline tool for production.<br><br>"
        "Originally created by Kickstand as a MEL code, it has now been modernized to Python 3, with added functionality.<br><br>"
        "For more information and API documentation, please refer to the "
        "<a href='https://stephenanimates.github.io/openPypelineStudio/index.html'>online documentation</a>."
    )
    ui = _get_ui()
    QtWidgets.QMessageBox.about(ui, "About openPypeline Studio", text)
