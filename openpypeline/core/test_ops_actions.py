"""Tests for shared project actions."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from openpypeline.core import ops_actions
from openpypeline.core.models import ItemContext


def test_save_master_saves_next_wip_before_master_and_reopens_it(
    monkeypatch,
    tmp_path,
):
    events = []
    master_path = tmp_path / "asset" / "asset_asset.ma"
    wip_path = tmp_path / "asset" / "wip" / "asset_wip_0002.ma"
    previous_wip_path = tmp_path / "asset" / "wip" / "asset_wip_0001.ma"
    previous_wip_path.parent.mkdir(parents=True)
    previous_wip_path.touch()

    def save_as(filepath, file_type):
        events.append(("save", filepath, file_type))
        return True

    def open_file(filepath):
        events.append(("open", filepath))
        return True

    dcc = SimpleNamespace(
        save_as=save_as,
        open=open_file,
    )
    monkeypatch.setattr(
        ops_actions,
        "OpsEngine",
        lambda: SimpleNamespace(file_handler=dcc),
    )
    monkeypatch.setattr(
        ops_actions.ops_info,
        "get_file_name",
        lambda _context, mode: {
            "master": str(master_path),
            "nextWorkshop": str(wip_path),
            "workshop": str(previous_wip_path),
        }[mode],
    )
    monkeypatch.setattr(
        ops_actions.prefs,
        "get_pref",
        lambda _key, default=None: "",
    )
    set_pref = MagicMock()
    monkeypatch.setattr(ops_actions.prefs, "set_pref", set_pref)

    assert ops_actions.save_master_file(
        ItemContext(tab=2, level1="characters", level2="asset"),
        {"comment": "Stable release"},
    )

    assert events == [
        ("save", str(wip_path), "mayaAscii"),
        ("save", str(master_path), "mayaAscii"),
        ("open", str(wip_path)),
    ]
    assert set_pref.call_args_list[0].args == (
        "ops_currOpenType",
        "workshop",
    )
    assert set_pref.call_args_list[1].args == (
        "ops_currOpenVersion",
        2,
    )


def test_save_master_does_not_publish_when_next_wip_save_fails(
    monkeypatch,
    tmp_path,
):
    master_path = tmp_path / "asset" / "asset_asset.ma"
    wip_path = tmp_path / "asset" / "wip" / "asset_wip_0002.ma"
    save_as = MagicMock(return_value=False)
    dcc = SimpleNamespace(save_as=save_as)
    monkeypatch.setattr(
        ops_actions,
        "OpsEngine",
        lambda: SimpleNamespace(file_handler=dcc),
    )
    monkeypatch.setattr(
        ops_actions.ops_info,
        "get_file_name",
        lambda _context, mode: {
            "master": str(master_path),
            "nextWorkshop": str(wip_path),
        }[mode],
    )

    assert not ops_actions.save_master_file(
        ItemContext(tab=2, level1="characters", level2="asset"),
        {},
    )

    save_as.assert_called_once_with(str(wip_path), "mayaAscii")


def test_save_master_publishes_to_the_selected_tracking_task(monkeypatch):
    from openpypeline.app.maya.core import tracker_factory

    publish_version = MagicMock(return_value=True)
    monkeypatch.setattr(
        tracker_factory,
        "get_tracker",
        lambda: SimpleNamespace(publish_version=publish_version),
    )
    monkeypatch.setattr(
        ops_actions,
        "save_master_file",
        lambda _context, _options: True,
    )
    monkeypatch.setattr(
        ops_actions.prefs,
        "get_pref",
        lambda _key, default=None: default,
    )
    monkeypatch.setattr(
        ops_actions.ops_info,
        "get_file_name",
        lambda _context, mode: f"/project/item/{mode}.ma",
    )

    assert ops_actions.save_master(
        "Stable release",
        False,
        False,
        1,
        task_id=42,
    )

    publish_version.assert_called_once_with(
        42,
        "/project/item/master.ma",
        0,
        "Stable release",
    )
