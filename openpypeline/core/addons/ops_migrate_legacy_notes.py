"""
File: ops_migrate_legacy_notes.py
Description: openPypeline Add-on for migrating legacy XML notes to JSON. Scans a project directory and safely translates info.xml and *Note.xml files.
"""

import os
import re
import json
from PySide6 import QtWidgets

ADDON_NAME = "Migrate Legacy Notes"

def get_xml_tag(xml_string, tag):
    """Helper to extract the data encapsulated by an XML tag."""
    match = re.search(f"<{tag}>(.*?)</{tag}>", xml_string, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def run():
    """Executes the note migration process."""
    # Prompt user for the root directory of the project
    msg = "Select the root folder of the Project you want to migrate notes for."
    dir_path = QtWidgets.QFileDialog.getExistingDirectory(None, msg)
    
    if not dir_path:
        return
        
    dir_path = dir_path.replace("\\", "/")
    
    info_count = 0
    history_count = 0
    errors = 0
    
    # Walk the directory tree looking for 'notes' folders
    for root, dirs, files in os.walk(dir_path):
        if os.path.basename(root) == "notes":
            for file_name in files:
                if not file_name.endswith(".xml"):
                    continue
                    
                file_path = os.path.join(root, file_name).replace("\\", "/")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    if file_name == "info.xml":
                        # Process Custom Notes (info.xml)
                        desc = get_xml_tag(content, "description")
                        desc = desc.replace("<br>", "\n")  # Convert legacy HTML breaks
                        
                        new_path = os.path.join(root, "info.json").replace("\\", "/")
                        with open(new_path, 'w', encoding='utf-8') as f:
                            json.dump({"description": desc}, f, indent=4)
                        info_count += 1
                        
                    elif file_name.endswith("Note.xml"):
                        # Process History Notes (*_AssetNote.xml, etc.)
                        notes_list = []
                        note_blocks = re.findall(r'<note>(.*?)</note>', content, re.IGNORECASE | re.DOTALL)
                        for block in note_blocks:
                            note_dict = {
                                "author": get_xml_tag(block, "author"),
                                "date": get_xml_tag(block, "date"),
                                "time": get_xml_tag(block, "time"),
                                "event": get_xml_tag(block, "event"),
                                "version": get_xml_tag(block, "version"),
                                "comment": get_xml_tag(block, "comment")
                            }
                            notes_list.append(note_dict)
                            
                        new_name = file_name.replace(".xml", ".json")
                        new_path = os.path.join(root, new_name).replace("\\", "/")
                        with open(new_path, 'w', encoding='utf-8') as f:
                            json.dump(notes_list, f, indent=4)
                        history_count += 1
                        
                except Exception as e:
                    print(f"Failed to migrate {file_path}: {e}")
                    errors += 1
                    
    # Display Success Report
    msg = (
        f"Note Migration Complete!\n\n"
        f"Converted {info_count} custom info.xml files.\n"
        f"Converted {history_count} history note files.\n\n"
        f"Your original XML files have been left intact as backups."
    )
    if errors:
        msg += f"\n\nEncountered {errors} errors. Check Maya's script editor for details."
        
    QtWidgets.QMessageBox.information(None, "Migration Successful", msg)