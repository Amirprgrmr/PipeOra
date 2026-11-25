from unittest.mock import patch

from app.core.paths import get_resource_path
from app.services.event_worker import EventWorker
from scripts.build_app import (
    build_pyinstaller_command,
    get_release_archive_name,
    normalize_arch,
    normalize_platform,
)


def test_resource_paths_exist():
    assert get_resource_path("resources", "icons", "pipeora.svg").exists()
    assert get_resource_path("ui", "styles", "style.qss").exists()


def test_event_worker_exits_gracefully_without_pactl():
    worker = EventWorker()
    with patch("app.services.event_worker.shutil.which", return_value=None):
        worker.run()
    assert worker._running is False


def test_cross_platform_build_plan():
    assert normalize_platform("linux") == "linux"
    assert normalize_platform("win32") == "windows"
    assert normalize_platform("darwin") == "macos"
    assert normalize_arch("AMD64") == "x86_64"
    assert normalize_arch("aarch64") == "arm64"

    assert get_release_archive_name("linux", "x86_64", "1.0.1") == "PipeOra-v1.0.1-linux-x86_64.tar.gz"
    assert get_release_archive_name("windows", "x86_64", "1.0.1") == "PipeOra-v1.0.1-windows-x86_64.zip"
    assert get_release_archive_name("macos", "arm64", "1.0.1") == "PipeOra-v1.0.1-macos-arm64.dmg"

    win_cmd = build_pyinstaller_command("windows")
    assert "--windowed" in win_cmd
    assert "--icon" in win_cmd
    assert any(";" in part for part in win_cmd)

    mac_cmd = build_pyinstaller_command("macos")
    assert "--osx-bundle-identifier" in mac_cmd
    assert "ir.amirprgrmr.pipeora" in mac_cmd

    linux_cmd = build_pyinstaller_command("linux")
    assert "--onedir" in linux_cmd
    assert any(":" in part for part in linux_cmd if "app/resources" in part)
