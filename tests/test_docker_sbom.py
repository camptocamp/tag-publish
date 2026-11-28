"""Test the Docker SBOM publishing."""

import subprocess
from typing import cast

import pytest

import tag_publish
from tag_publish.configuration import DockerImage, DockerRepository
from tag_publish.publish import docker

_DIGEST = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


class Calls:
    """Record the subprocess calls and the downloaded applications."""

    def __init__(self) -> None:
        self.commands: list[list[str]] = []
        self.applications: list[str] = []

    def run(self, command: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.commands.append(list(command))
        stdout = ""
        if command[0] == "docker" and len(command) > 1 and command[1] == "push":
            stdout = f"1.2.3: digest: {_DIGEST} size: 855\n"
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

    def download(self, application_name: str, *args: object, **kwargs: object) -> None:
        self.applications.append(application_name)


def _run_docker(monkeypatch: pytest.MonkeyPatch, image_config: DockerImage) -> Calls:
    calls = Calls()

    monkeypatch.setattr(subprocess, "run", calls.run)
    monkeypatch.setattr(tag_publish, "download_application", calls.download)

    images_full: list[str] = []
    success = docker(
        cast("DockerRepository", {"host": "ghcr.io"}),
        "github",
        image_config,
        "latest",
        ["1.2.3"],
        images_full,
    )
    assert success
    assert images_full == ["ghcr.io/camptocamp/example:1.2.3"]
    return calls


def test_docker_publishes_sbom_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _run_docker(monkeypatch, cast("DockerImage", {"name": "camptocamp/example"}))

    assert calls.applications == ["anchore/syft", "sigstore/cosign"]

    syft = [command for command in calls.commands if command[0] == "syft"]
    assert len(syft) == 1
    assert syft[0][:2] == ["syft", "docker:camptocamp/example:latest"]
    assert syft[0][2].startswith("--output=cyclonedx-json=")

    cosign = [command for command in calls.commands if command[0] == "cosign"]
    assert len(cosign) == 1
    assert cosign[0][0:2] == ["cosign", "attest"]
    assert "--type=cyclonedx" in cosign[0]
    assert any(argument.startswith("--predicate=") for argument in cosign[0])
    assert "--yes" in cosign[0]
    assert cosign[0][-1] == f"ghcr.io/camptocamp/example@{_DIGEST}"


def test_docker_sbom_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _run_docker(monkeypatch, cast("DockerImage", {"name": "camptocamp/example", "sbom": False}))

    assert calls.applications == []
    assert not any(command[0] in ("syft", "cosign") for command in calls.commands)
