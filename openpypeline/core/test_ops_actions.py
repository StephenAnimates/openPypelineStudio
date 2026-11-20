"""Tests for shared project actions.

:File: test_ops_actions.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from openpypeline.core import ops_actions
from openpypeline.core.models import ItemContext


def test_save_master_saves_next_wip_before_master_and_reopens_it(
    monkeypatch,
    tmp_path,
):
    """Save the next WIP before publishing master, then reopen that WIP."""
    events = []
    master_path = tmp_path / "asset" / "asset_asset.ma"
    wip_path = tmp_path / "asset" / "wip" / "asset_wip_0002.ma"
    previous_wip_path = tmp_path / "asset" / "wip" / "asset_wip_0001.ma"
    previous_wip_path.parent.mkdir(parents=True)
    previous_wip_path.touch()

    def save_as(filepath, file_type):
        """Record a DCC save request for order verification."""
        events.append(("save", filepath, file_type))
        return True

    def open_file(filepath):
        """Record a DCC open request for order verification."""
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


@pytest.mark.parametrize(
    ("file_ext", "expected_file_type"),
    [
        ("usd", "USD Export"),
        ("usda", "USD Export"),
        ("abc", "Alembic"),
    ],
)
def test_save_master_file_export_formats(
    monkeypatch,
    tmp_path,
    file_ext: str,
    expected_file_type: str,
) -> None:
    """Verify OpenUSD and Alembic formats call ``export_file`` during master save."""
    master_path = tmp_path / f"master.{file_ext}"
    next_wip_path = tmp_path / f"asset_v002.{file_ext}"

    mock_file_handler = MagicMock()
    mock_file_handler.get_file_type.return_value = None
    mock_file_handler.export_file.return_value = True
    mock_file_handler.open.return_value = True

    mock_engine = MagicMock()
    mock_engine.file_handler = mock_file_handler

    monkeypatch.setattr(ops_actions, "OpsEngine", lambda: mock_engine)
    monkeypatch.setattr(
        ops_actions.ops_info,
        "get_file_name",
        lambda _ctx, kind: str(master_path if kind == "master" else next_wip_path),
    )
    monkeypatch.setattr(ops_actions.ops_info, "get_version_from_file", lambda _p: 2)
    monkeypatch.setattr(ops_actions.prefs, "get_pref", lambda _k, default="": default)
    monkeypatch.setattr(ops_actions.prefs, "set_pref", lambda _k, _v: None)

    result = ops_actions.save_master_file(
        ItemContext(tab=2, level1="characters", level2="asset"),
        {"comment": "Publish export", "after": 1},
    )

    assert result is True
    mock_file_handler.export_file.assert_any_call(
        str(next_wip_path), expected_file_type, selected=False
    )
    mock_file_handler.export_file.assert_any_call(
        str(master_path), expected_file_type, selected=False
    )


def test_save_master_does_not_publish_when_next_wip_save_fails(
    monkeypatch,
    tmp_path,
):
    """Abort master publishing when the next WIP cannot be saved."""
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
    """Publish the saved master against the explicitly selected tracker task."""
    from openpypeline.core import tracker_factory

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
