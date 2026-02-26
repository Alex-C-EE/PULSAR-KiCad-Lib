#!/usr/bin/env python3
"""
PULSAR KiCad Library Packaging Script

Builds a PCM-compatible ZIP archive and updates docs/packages.json
with the correct SHA256 hash, download size, and install size.

Usage:
    python scripts/package.py [--version 1.0.0] [--tag v1.0.0]
"""

import argparse
import hashlib
import json
import os
import zipfile
from pathlib import Path


def get_repo_root() -> Path:
    """Get the repository root directory."""
    return Path(__file__).resolve().parent.parent


def compute_install_size(directories: list[Path]) -> int:
    """Compute total uncompressed size of all files to be archived."""
    total = 0
    for d in directories:
        if d.is_dir():
            for f in d.rglob("*"):
                if f.is_file():
                    total += f.stat().st_size
        elif d.is_file():
            total += d.stat().st_size
    return total


def create_zip_archive(output_path: Path, root: Path) -> Path:
    """Create a PCM-compatible ZIP archive.

    The archive contains:
        metadata.json
        resources/icon.png
        symbols/*.kicad_sym
        footprints/PULSAR.pretty/*.kicad_mod
        3dmodels/PULSAR.3dshapes/*.stp
    """
    items_to_include = [
        root / "metadata.json",
        root / "resources",
        root / "symbols",
        root / "footprints",
        root / "3dmodels",
    ]

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for item in items_to_include:
            if item.is_file():
                arcname = item.relative_to(root).as_posix()
                zf.write(item, arcname)
            elif item.is_dir():
                for file_path in sorted(item.rglob("*")):
                    if file_path.is_file():
                        arcname = file_path.relative_to(root).as_posix()
                        zf.write(file_path, arcname)

    return output_path


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def update_packages_json(
    packages_json_path: Path,
    version: str,
    tag: str,
    sha256: str,
    download_size: int,
    install_size: int,
) -> None:
    """Update docs/packages.json with download metadata for the given version."""
    with open(packages_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    download_url = (
        f"https://github.com/Alex-C-EE/PULSAR-KiCad-Lib/releases/download/{tag}/"
        f"PULSAR-KiCad-Lib-{version}.zip"
    )

    new_version_entry = {
        "version": version,
        "status": "stable",
        "kicad_version": "8.0",
        "download_url": download_url,
        "download_sha256": sha256,
        "download_size": download_size,
        "install_size": install_size,
    }

    # Update the first (and only) package
    pkg = data["packages"][0]
    # Replace or append version
    versions = pkg.get("versions", [])
    updated = False
    for i, v in enumerate(versions):
        if v["version"] == version:
            versions[i] = new_version_entry
            updated = True
            break
    if not updated:
        versions.append(new_version_entry)
    pkg["versions"] = versions

    with open(packages_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.write("\n")

    print(f"Updated {packages_json_path}")


def update_metadata_json(metadata_path: Path, version: str) -> None:
    """Update the version in the in-archive metadata.json."""
    with open(metadata_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["versions"] = [
        {
            "version": version,
            "status": "stable",
            "kicad_version": "8.0",
        }
    ]

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.write("\n")

    print(f"Updated {metadata_path}")


def main():
    parser = argparse.ArgumentParser(description="Package PULSAR KiCad Library for PCM")
    parser.add_argument("--version", default="1.0.0", help="Version string (e.g. 1.0.0)")
    parser.add_argument("--tag", default=None, help="Git tag (e.g. v1.0.0). Defaults to v{version}")
    args = parser.parse_args()

    version = args.version
    tag = args.tag or f"v{version}"
    root = get_repo_root()
    output_zip = root / f"PULSAR-KiCad-Lib-{version}.zip"

    print(f"Packaging PULSAR KiCad Library v{version}...")
    print(f"  Repository root: {root}")

    # Update in-archive metadata version
    update_metadata_json(root / "metadata.json", version)

    # Compute install size before zipping
    install_size = compute_install_size([
        root / "metadata.json",
        root / "resources",
        root / "symbols",
        root / "footprints",
        root / "3dmodels",
    ])

    # Create ZIP
    create_zip_archive(output_zip, root)
    download_size = output_zip.stat().st_size
    sha256 = compute_sha256(output_zip)

    print(f"\n  Output:       {output_zip}")
    print(f"  SHA256:       {sha256}")
    print(f"  Download size: {download_size:,} bytes")
    print(f"  Install size:  {install_size:,} bytes")

    # Update packages.json
    packages_json = root / "docs" / "packages.json"
    update_packages_json(packages_json, version, tag, sha256, download_size, install_size)

    # Validate ZIP structure
    print("\nValidating ZIP structure...")
    with zipfile.ZipFile(output_zip, "r") as zf:
        names = zf.namelist()
        required = ["metadata.json"]
        required_prefixes = ["symbols/", "footprints/"]
        for req in required:
            if req not in names:
                print(f"  WARNING: Missing required file: {req}")
        for prefix in required_prefixes:
            if not any(n.startswith(prefix) for n in names):
                print(f"  WARNING: Missing required directory: {prefix}")
        print(f"  Archive contains {len(names)} files")
        print("  Structure looks good!" if all(
            req in names for req in required
        ) and all(
            any(n.startswith(p) for n in names) for p in required_prefixes
        ) else "  WARNING: Archive may have issues")

    print(f"\nDone! Upload {output_zip.name} as a GitHub Release asset for tag {tag}")


if __name__ == "__main__":
    main()
