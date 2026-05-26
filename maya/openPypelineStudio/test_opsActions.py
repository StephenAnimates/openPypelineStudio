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

import opsActions

# TODO: Write automated tests to verify that OpenUSD (.usd/.usda) and Alembic (.abc) 
#       file formats trigger the correct `export_file` calls in opsActions.

@patch('opsProject.get_projects_data', return_value=[])
@patch('opsProject.rewrite_proj_file')
@patch('maya.cmds.optionVar')
def test_create_new_project(mock_optionVar, mock_rewrite, mock_get_data, tmp_path):
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
    new_workshop_name = "wip"
    new_workshop_format = "ma"
    
    # Sub-folder names
    new_lib_loc = "lib"
    new_shot_loc = "scenes"
    new_renders_loc = "renders"
    new_scripts_loc = "scripts"
    new_textures_loc = "textures"
    new_particles_loc = "particles"
    new_archive_loc = "archive"
    new_deleted_loc = "deleted"
    new_users = ""
    user_mode = "0"

    # Mock the current project name so it doesn't try to switch projects automatically
    mock_optionVar.return_value = ""

    # 2. Execute the function
    result = opsActions.create_or_edit_project(
        mode, old_name, new_name, new_path, new_description, new_status, new_date, new_deadline,
        new_master_name, new_master_format, new_workshop_name, new_workshop_format, new_lib_loc,
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