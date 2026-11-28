"""Test the Helm OCI signing."""

import subprocess
from pathlib import Path
from typing import cast

import pytest

import tag_publish
from tag_publish.configuration import HelmOci
from tag_publish.publish import helm

_DIGEST = "sha256:1111111111111111111111111111111111111111111111111111111111111111"


class Calls:
    """Record the subprocess calls made by the Helm publishing."""

    def __init__(self) -> None:
        self.commands: list[list[str]] = []

    def run(self, command: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.commands.append(list(command))
        stdout = ""
        if command[:2] == ["helm", "push"]:
            stdout = f"Pushed: ghcr.io/camptocamp/example/test:1.2.3\nDigest: {_DIGEST}\n"
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")


def _run_helm(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    oci_config: HelmOci | None,
) -> Calls:
    (tmp_path / "Chart.yaml").write_text("name: test\nversion: 0.0.0\n", encoding="utf-8")
    package_dir = tmp_path / ".cr-release-packages"
    package_dir.mkdir()
    (package_dir / "test-1.2.3.tgz").touch()

    calls = Calls()
    monkeypatch.setattr(subprocess, "run", calls.run)
    monkeypatch.setattr(tag_publish, "download_application", lambda *_args, **_kwargs: None)
    monkeypatch.chdir(tmp_path)

    success = helm(
        str(tmp_path),
        "1.2.3",
        "camptocamp",
        "example",
        "abcdef",
        "token",
        oci_config=oci_config,
        publish_types=cast("list[str]", ["oci"]),
    )
    assert success
    return calls


def test_helm_signs_with_digest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls = _run_helm(monkeypatch, tmp_path, cast("HelmOci", {"enabled": True, "sign": True}))

    sign = [command for command in calls.commands if command[:2] == ["cosign", "sign"]]
    assert len(sign) == 1
    assert sign[0][2] == f"ghcr.io/camptocamp/example/test@{_DIGEST}"


def test_helm_oci_without_signing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls = _run_helm(monkeypatch, tmp_path, cast("HelmOci", {"enabled": True, "sign": False}))

    assert not any(command[:2] == ["cosign", "sign"] for command in calls.commands)
