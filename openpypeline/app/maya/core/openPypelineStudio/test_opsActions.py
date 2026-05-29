"""
File: test_opsActions.py
Description: Unit tests for the core openPypeline Studio actions.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the legacy backend directory to the sys.path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../maya/openPypelineStudio')))

import openpypeline.app.maya.core.openPypelineStudio.opsActions as opsActions

@pytest.mark.parametrize("file_ext, expected_file_type", [
    ("usd", "USD Export"),
    ("usda", "USD Export"),
    ("abc", "Alembic"),
])
@patch('os.makedirs')
@patch('os.path.isdir')
@patch('opsInfo.get_file_name')
@patch('opsInfo.get_category')
@patch('openpypeline.core.util.prefs.get_pref')
@patch('opsEngine.OpsEngine')
def test_create_new_item_export_formats(mock_OpsEngine, mock_get_pref, mock_get_category, mock_get_file_name, mock_isdir, mock_makedirs, file_ext, expected_file_type):
    """
    Test that OpenUSD and Alembic file formats trigger the correct 
    `export_file` calls during item creation (mode 2 and 3).
    """
    mock_engine_instance = MagicMock()
    mock_file_handler = MagicMock()
    mock_engine_instance.file_handler = mock_file_handler
    mock_OpsEngine.return_value = mock_engine_instance
    
    def mock_get_pref_call(key, default=None):
        if key == "ops_wipFormat": return file_ext
        if key == "ops_wip": return "wip"
        return default or "mocked_value"
    mock_get_pref.side_effect = mock_get_pref_call

    def mock_get_file_name_call(tab, level1, level2, level3, file_type, *args, **kwargs):
        if file_type == 'folder': return "/dummy/path/item"
        if file_type == 'parentFolder': return "/dummy/path"
        if file_type == 'nextWorkshop': return f"/dummy/path/item/item_v001.{file_ext}"
        return "/dummy/path/other"
    mock_get_file_name.side_effect = mock_get_file_name_call
    
    def mock_isdir_call(path):
        if path == "/dummy/path/item": return False
        if path == "/dummy/path": return True
        return True
    mock_isdir.side_effect = mock_isdir_call
    
    mock_get_category.return_value = "Asset"

    with patch('opsActions.add_event_note'), patch('opsActions.set_custom_notes'):
        # Mode 2 is export selection
        opsActions.create_new_item(2, "char", "hero", "", 2)
        mock_file_handler.export_file.assert_called_with(f"/dummy/path/item/item_v001.{file_ext}", expected_file_type, selected=True)
        
        # Mode 3 is export all
        opsActions.create_new_item(2, "char", "hero", "", 3)
        mock_file_handler.export_file.assert_called_with(f"/dummy/path/item/item_v001.{file_ext}", expected_file_type, selected=False)


@pytest.mark.parametrize("file_ext, expected_file_type", [
    ("usd", "USD Export"),
    ("usda", "USD Export"),
    ("abc", "Alembic"),
])
@patch('opsInfo.get_version_from_file', return_value=1)
@patch('opsInfo.get_file_name')
@patch('openpypeline.core.util.prefs.get_pref')
@patch('opsEngine.OpsEngine')
def test_save_wip_export_formats(mock_OpsEngine, mock_get_pref, mock_get_file_name, mock_get_version, file_ext, expected_file_type):
    """
    Test that save_wip triggers the correct `export_file` calls for OpenUSD and Alembic.
    """
    mock_engine_instance = MagicMock()
    mock_file_handler = MagicMock()
    mock_engine_instance.file_handler = mock_file_handler
    mock_OpsEngine.return_value = mock_engine_instance
    
    def mock_get_pref_call(key, default=None):
        if key == "ops_wipFormat": return file_ext
        if key == "ops_wip": return "wip"
        return default or "mocked_value"
    mock_get_pref.side_effect = mock_get_pref_call
    
    def mock_get_file_name_call(tab, level1, level2, level3, file_type, *args, **kwargs):
        if file_type == 'nextWorkshop': return f"/dummy/path/item/item_v001.{file_ext}"
        return "/dummy/path/other"
    mock_get_file_name.side_effect = mock_get_file_name_call

    with patch('opsActions.add_event_note'):
        opsActions.save_wip("test note")
        mock_file_handler.export_file.assert_called_once_with(f"/dummy/path/item/item_v001.{file_ext}", expected_file_type, selected=False)


@pytest.mark.parametrize("file_ext, expected_file_type", [
    ("usd", "USD Export"),
    ("usda", "USD Export"),
    ("abc", "Alembic"),
])
@patch('os.rename')
@patch('os.path.exists', return_value=False)
@patch('opsActions.save_wip')
@patch('opsInfo.get_file_name')
@patch('openpypeline.core.util.prefs.get_pref')
@patch('opsEngine.OpsEngine')
def test_save_master_export_formats(mock_OpsEngine, mock_get_pref, mock_get_file_name, mock_save_wip, mock_exists, mock_rename, file_ext, expected_file_type):
    """
    Test that save_master triggers the correct `export_file` calls for OpenUSD and Alembic.
    """
    mock_engine_instance = MagicMock()
    mock_file_handler = MagicMock()
    mock_engine_instance.file_handler = mock_file_handler
    mock_OpsEngine.return_value = mock_engine_instance
    
    def mock_get_pref_call(key, default=None):
        if key == "ops_wipFormat": return file_ext
        if key == "ops_masterFormat": return file_ext
        if key == "ops_masterName": return "master"
        return default or "mocked_value"
    mock_get_pref.side_effect = mock_get_pref_call
    
    def mock_get_file_name_call(tab, level1, level2, level3, file_type, *args, **kwargs):
        if file_type == 'master': return f"/dummy/path/item/master.{file_ext}"
        if file_type == 'nextVersion': return f"/dummy/path/item/item_v001.{file_ext}"
        return "/dummy/path/other"
    mock_get_file_name.side_effect = mock_get_file_name_call

    with patch('opsActions.add_event_note'):
        opsActions.save_master("test note", 0, 0, 0)
        mock_file_handler.export_file.assert_called_once_with(f"/dummy/path/item/master.{file_ext}", expected_file_type, selected=False)

@patch('opsProject.get_projects_data', return_value=[])
@patch('opsProject.rewrite_proj_file')
@patch('openpypeline.core.util.prefs.get_pref')
def test_create_new_project(mock_get_pref, mock_rewrite, mock_get_data, tmp_path):
    """
    Test that opsActions.create_or_edit_project successfully handles 
    creating a new project (mode 0), making the necessary directories, 
    and generating the correct XML string for the database.
    """
    
    # 1. Setup Test Data
    mode = 0  # 0 indicates "Create New Project"
    old_name = ""
    new_name = "TestProject"
    
    # Use the safe, temporary pytest directory for the project path
    new_path = str(tmp_path / "TestProject").replace("\\", "/")
    
    new_description = "A pytest generated project"
    new_status = "1"
    new_date = "01/01/2026"
    new_deadline = "12/31/2026"
    new_master_name = "master"
    new_master_format = "ma"
    new_wip_name = "wip"
    new_wip_format = "ma"
    
    # Sub-folder names
    new_lib_loc = "scenes/assets"
    new_shot_loc = "scenes"
    new_renders_loc = "images/renders"
    new_scripts_loc = "scripts"
    new_textures_loc = "sourceimages"
    new_particles_loc = "particles"
    new_archive_loc = "archive"
    new_deleted_loc = "deleted"
    new_users = ""
    user_mode = "0"

    # Mock the current project name preference so it doesn't try to switch projects automatically
    mock_get_pref.return_value = ""

    # 2. Execute the function
    result = opsActions.create_or_edit_project(
        mode, old_name, new_name, new_path, new_description, new_status, new_date, new_deadline,
        new_master_name, new_master_format, new_wip_name, new_wip_format, new_lib_loc,
        new_shot_loc, new_renders_loc, new_scripts_loc, new_textures_loc, new_particles_loc,
        new_archive_loc, new_deleted_loc, new_users, user_mode
    )

    # 3. Assertions (Did it behave correctly?)
    assert result == 1, "Project creation should return 1 for success."
    
    # Verify that the directory and all of its sub-directories were successfully created on disk
    assert os.path.exists(new_path)
    assert os.path.exists(os.path.join(new_path, new_shot_loc))
    assert os.path.exists(os.path.join(new_path, new_archive_loc))
    
    # Verify that it attempted to write the new project to the XML database
    assert mock_rewrite.called
    written_xml_data = mock_rewrite.call_args[0][0]
    assert len(written_xml_data) == 1
    assert f"<name>{new_name}</name>" in written_xml_data[0]