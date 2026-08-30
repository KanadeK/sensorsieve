"""Build deterministic source/example assets and a checksum manifest for a tag."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
TIMESTAMP = (2024, 1, 2, 3, 4, 6)


def _version() -> str:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    return str(project["version"])


def _zip_tree(output: Path, roots: tuple[Path, ...]) -> Path:
    with zipfile.ZipFile(output, "w") as archive:
        for root in roots:
            for source in sorted(path for path in root.rglob("*") if path.is_file()):
                relative = source.relative_to(ROOT).as_posix()
                info = zipfile.ZipInfo(relative, date_time=TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o644 << 16
                archive.writestr(info, source.read_bytes())
    return output


def _checksums(assets: tuple[Path, ...]) -> Path:
    output = DIST / "SHA256SUMS"
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}"
        for path in sorted(assets, key=lambda item: item.name)
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return output


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: package_release.py vVERSION")
    version = _version()
    tag = sys.argv[1]
    if tag != f"v{version}":
        raise SystemExit(f"tag {tag} does not match project version {version}")

    wheel = DIST / f"sensorsieve-{version}-py3-none-any.whl"
    source_distribution = DIST / f"sensorsieve-{version}.tar.gz"
    if not wheel.is_file() or not source_distribution.is_file():
        raise SystemExit("run uv build before packaging release assets")

    examples = _zip_tree(
        DIST / f"sensorsieve-{version}-examples.zip",
        (ROOT / "examples", ROOT / "docs" / "demo"),
    )
    source_archive = DIST / f"sensorsieve-{version}-source.zip"
    subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT.as_posix()}",
            "archive",
            "--format=zip",
            f"--prefix=sensorsieve-{version}/",
            f"--output={source_archive}",
            tag,
        ],
        cwd=ROOT,
        check=True,
    )
    print(_checksums((wheel, source_distribution, examples, source_archive)))


if __name__ == "__main__":
    main()
