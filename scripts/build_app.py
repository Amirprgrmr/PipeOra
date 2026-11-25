#!/usr/bin/env python3
"""
اسکریپت ساخت بسته اجرایی مستقل PipeOra برای سه سیستم‌عامل (Linux, Windows, macOS)
استفاده از PyInstaller و بسته‌بندی بومی متناسب با هر پلتفرم
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import __version__


def normalize_platform(raw_platform: Optional[str] = None) -> str:
    """استانداردسازی نام سیستم‌عامل به یکی از سه مقدار linux، windows یا macos."""
    target = (raw_platform or sys.platform).lower()
    if target.startswith("linux"):
        return "linux"
    if target.startswith("win"):
        return "windows"
    if target in ("darwin", "macos", "osx"):
        return "macos"
    raise ValueError(f"پلتفرم پشتیبانی‌نشده: {target}")


def normalize_arch(raw_arch: Optional[str] = None) -> str:
    """استانداردسازی نام معماری پردازنده."""
    arch = (raw_arch or platform.machine() or "x86_64").lower()
    if arch in ("amd64", "x86_64", "x64"):
        return "x86_64"
    if arch in ("aarch64", "arm64"):
        return "arm64"
    return arch


def get_release_archive_name(target_os: str, arch: str, version: str = __version__) -> str:
    """تعیین نام رسمی خروجی نهایی متناسب با سیستم‌عامل."""
    if target_os == "linux":
        return f"PipeOra-v{version}-linux-{arch}.tar.gz"
    if target_os == "windows":
        return f"PipeOra-v{version}-windows-{arch}.zip"
    if target_os == "macos":
        return f"PipeOra-v{version}-macos-{arch}.dmg"
    raise ValueError(f"پلتفرم نامعتبر: {target_os}")


def prepare_macos_icns(build_dir: Path) -> Optional[Path]:
    """ساخت فایل آیکون macOS (.icns) با ابزار بومی iconutil از روی PNGهای رسمی."""
    iconset_dir = build_dir / "PipeOra.iconset"
    iconset_dir.mkdir(parents=True, exist_ok=True)
    icons_base = PROJECT_ROOT / "packaging" / "icons"

    mapping = {
        "icon_16x16.png": icons_base / "16x16" / "pipeora.png",
        "icon_16x16@2x.png": icons_base / "32x32" / "pipeora.png",
        "icon_32x32.png": icons_base / "32x32" / "pipeora.png",
        "icon_32x32@2x.png": icons_base / "64x64" / "pipeora.png",
        "icon_128x128.png": icons_base / "128x128" / "pipeora.png",
        "icon_128x128@2x.png": icons_base / "256x256" / "pipeora.png",
        "icon_256x256.png": icons_base / "256x256" / "pipeora.png",
        "icon_256x256@2x.png": icons_base / "512x512" / "pipeora.png",
        "icon_512x512.png": icons_base / "512x512" / "pipeora.png",
    }

    for dest_name, src in mapping.items():
        if src.exists():
            shutil.copy2(src, iconset_dir / dest_name)

    icns_path = build_dir / "pipeora.icns"
    if shutil.which("iconutil"):
        res = subprocess.run(
            ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(icns_path)],
            check=False,
        )
        if res.returncode == 0 and icns_path.exists():
            return icns_path
    return None


def build_pyinstaller_command(
    target_os: str,
    python_exe: str = sys.executable,
    icon_path: Optional[Path] = None,
) -> List[str]:
    """ساخت لیست آرگومان‌های استاندارد PyInstaller برای سیستم‌عامل هدف."""
    sep = ";" if target_os == "windows" else ":"
    cmd = [
        python_exe,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onedir",
        "--name",
        "PipeOra",
        "--paths",
        str(PROJECT_ROOT),
        "--add-data",
        f"{PROJECT_ROOT / 'app' / 'resources'}{sep}app/resources",
        "--add-data",
        f"{PROJECT_ROOT / 'app' / 'ui' / 'styles' / 'style.qss'}{sep}app/ui/styles",
        "--add-data",
        f"{PROJECT_ROOT / 'packaging'}{sep}packaging",
        "--collect-submodules",
        "app",
        "--hidden-import",
        "PySide6.QtSvg",
        "--hidden-import",
        "PySide6.QtNetwork",
    ]

    if target_os == "windows":
        win_icon = icon_path or (PROJECT_ROOT / "packaging" / "pipeora.ico")
        cmd.extend(["--icon", str(win_icon)])
    elif target_os == "macos":
        cmd.extend(["--osx-bundle-identifier", "ir.amirprgrmr.pipeora"])
        if icon_path:
            cmd.extend(["--icon", str(icon_path)])

    cmd.append(str(PROJECT_ROOT / "app" / "main.py"))
    return cmd


def _copy_common_metadata(target_dir: Path) -> None:
    """کپی فایل‌های مستندات و لایسنس کنار بسته خروجی."""
    for fname in ("README.md", "LICENSE"):
        src = PROJECT_ROOT / fname
        if src.exists():
            shutil.copy2(src, target_dir / fname)


def package_output(target_os: str, arch: str, dist_dir: Path, version: str = __version__) -> Path:
    """بسته‌بندی خروجی PyInstaller متناسب با هر سیستم‌عامل."""
    archive_name = get_release_archive_name(target_os, arch, version)
    archive_path = dist_dir / archive_name

    if target_os == "linux":
        bundle_dir = dist_dir / "PipeOra"
        _copy_common_metadata(bundle_dir)
        for pkg_file in ("pipeora.desktop", "pipeora.svg"):
            src = PROJECT_ROOT / "packaging" / pkg_file
            if src.exists():
                shutil.copy2(src, bundle_dir / pkg_file)

        if archive_path.exists():
            archive_path.unlink()
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(bundle_dir, arcname="PipeOra")
        return archive_path

    if target_os == "windows":
        bundle_dir = dist_dir / "PipeOra"
        _copy_common_metadata(bundle_dir)
        if archive_path.exists():
            archive_path.unlink()
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for item in bundle_dir.rglob("*"):
                if item.is_file():
                    zf.write(item, arcname=str(Path("PipeOra") / item.relative_to(bundle_dir)))
        return archive_path

    # macOS (.app -> .dmg یا .zip در صورت نبود hdiutil)
    app_bundle = dist_dir / "PipeOra.app"
    if archive_path.exists():
        archive_path.unlink()
    if shutil.which("hdiutil"):
        staging = dist_dir / "_dmg_staging"
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True, exist_ok=True)
        shutil.copytree(app_bundle, staging / "PipeOra.app", symlinks=True)
        applications_link = staging / "Applications"
        if not applications_link.exists():
            applications_link.symlink_to("/Applications")
        subprocess.run(
            [
                "hdiutil",
                "create",
                "-volname",
                f"PipeOra v{version}",
                "-srcfolder",
                str(staging),
                "-ov",
                "-format",
                "UDZO",
                str(archive_path),
            ],
            check=True,
        )
        shutil.rmtree(staging, ignore_errors=True)
        return archive_path

    zip_fallback = dist_dir / f"PipeOra-v{version}-macos-{arch}.zip"
    shutil.make_archive(str(zip_fallback.with_suffix("")), "zip", root_dir=dist_dir, base_dir="PipeOra.app")
    return zip_fallback


def smoke_test_binary(target_os: str, dist_dir: Path) -> None:
    """تست اجرای سریع باینری ساخته‌شده با فلگ --version."""
    if target_os == "linux":
        exe = dist_dir / "PipeOra" / "PipeOra"
    elif target_os == "windows":
        exe = dist_dir / "PipeOra" / "PipeOra.exe"
    else:
        exe = dist_dir / "PipeOra.app" / "Contents" / "MacOS" / "PipeOra"

    if not exe.exists():
        raise FileNotFoundError(f"فایل اجرایی ساخته‌شده یافت نشد: {exe}")

    res = subprocess.run([str(exe), "--version"], capture_output=True, text=True, check=False, timeout=20)
    if res.returncode != 0:
        raise RuntimeError(f"اجرای --version ناموفق بود (exit={res.returncode}): {res.stderr}")
    print(f"[SMOKE OK] {exe} -> {res.stdout.strip() or '(windowed exit 0)'}")


def main() -> int:
    parser = argparse.ArgumentParser(description="ساخت نسخه مستقل اجرایی PipeOra برای Linux / Windows / macOS")
    parser.add_argument("--platform", choices=["linux", "windows", "macos"], help="سیستم‌عامل هدف (پیش‌فرض: سیستم فعلی)")
    parser.add_argument("--arch", help="معماری پردازنده (پیش‌فرض: سیستم فعلی)")
    parser.add_argument("--dry-run", action="store_true", help="نمایش دستور و مسیر خروجی بدون اجرای واقعی بیلد")
    parser.add_argument("--skip-smoke", action="store_true", help="صرف‌نظر از تست --version پس از بیلد")
    args = parser.parse_args()

    target_os = normalize_platform(args.platform)
    arch = normalize_arch(args.arch)
    dist_dir = PROJECT_ROOT / "dist"
    build_dir = PROJECT_ROOT / "build"

    icon_path: Optional[Path] = None
    if target_os == "macos" and not args.dry_run:
        build_dir.mkdir(parents=True, exist_ok=True)
        icon_path = prepare_macos_icns(build_dir)

    cmd = build_pyinstaller_command(target_os, icon_path=icon_path)
    expected_archive = get_release_archive_name(target_os, arch)

    if args.dry_run:
        print(f"Target OS : {target_os} ({arch})")
        print(f"Archive   : {dist_dir / expected_archive}")
        print(f"Command   : {' '.join(cmd)}")
        return 0

    print(f"شروع ساخت نسخه مستقل PipeOra v{__version__} برای {target_os} ({arch})...")
    subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)

    if not args.skip_smoke:
        smoke_test_binary(target_os, dist_dir)

    artifact = package_output(target_os, arch, dist_dir)
    print(f"بسته نهایی با موفقیت ساخته شد: {artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
