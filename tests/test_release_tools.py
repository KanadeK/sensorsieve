from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import scripts.package_release as package_release

ROOT = Path(__file__).resolve().parent.parent


def _git(repo: Path, *arguments: str) -> None:
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=SensorSieve Test",
            "-c",
            "user.email=test@example.invalid",
            *arguments,
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def test_release_packager_requires_annotated_tag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    (repo / "README.md").write_text("release fixture\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "test fixture")
    _git(repo, "tag", "v0.1.0")
    monkeypatch.setattr(package_release, "ROOT", repo)

    with pytest.raises(SystemExit, match="must be annotated"):
        package_release._require_annotated_tag("v0.1.0")

    _git(repo, "tag", "-d", "v0.1.0")
    _git(repo, "tag", "-a", "v0.1.0", "-m", "Release v0.1.0")
    package_release._require_annotated_tag("v0.1.0")


def test_release_workflow_gates_tag_and_keeps_assets_immutable() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "windows-latest" in workflow
    assert "needs: quality" in workflow
    assert "git cat-file -t" in workflow
    assert "git merge-base --is-ancestor" in workflow
    assert "--clobber" not in workflow
