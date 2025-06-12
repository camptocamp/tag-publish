"""Tag Publish main module."""

import base64
import json
import os
import pkgutil
import re
import subprocess  # nosec
from pathlib import Path
from re import Match, Pattern
from typing import Any, Optional, TypedDict, cast, overload

import applications_download
import githubkit
import githubkit.versions.latest.models
import jsonschema_validator
import ruamel.yaml
import security_md
import yaml

import tag_publish.configuration

VersionTransform = TypedDict(
    "VersionTransform",
    {
        # The from regular expression
        "from": Pattern[str],
        # The expand regular expression: https://docs.python.org/3/library/re.html#re.Match.expand
        "to": str,
    },
    total=False,
)


class GH:
    """GitHub helper class."""

    def __init__(self) -> None:
        """Initialize the GitHub helper class."""
        token = (
            os.environ["GITHUB_TOKEN"]
            if "GITHUB_TOKEN" in os.environ
            else subprocess.run(
                ["gh", "auth", "token"],
                check=True,
                stdout=subprocess.PIPE,
                encoding="utf-8",
            ).stdout.strip()
        )
        self.github = githubkit.GitHub(token)

        # Get repository information
        repo_name = (
            os.environ["GITHUB_REPOSITORY"]
            if "GITHUB_REPOSITORY" in os.environ
            else subprocess.run(
                ["gh", "repo", "view", "--json", "name,owner", "--jq", '(.owner.login + "/" + .name)'],
                check=True,
                stdout=subprocess.PIPE,
                encoding="utf-8",
            ).stdout.strip()
        )

        # Split owner and repository name
        self.owner, self.repository = repo_name.split("/")

        # Get repository data and default branch
        repo = self.github.rest.repos.get(
            owner=self.owner,
            repo=self.repository,
        ).parsed_data

        self.default_branch = repo.default_branch


def get_security_md(gh: GH, local: bool) -> security_md.Security:
    """
    Get the SECURITY.md file.

    Arguments:
        gh: The GitHub helper
        local: If we should use the local file

    """
    if local:
        if Path("SECURITY.md").exists():
            print("Using the local SECURITY.md file")
            with Path("SECURITY.md").open(encoding="utf-8") as open_file:
                return security_md.Security(open_file.read())
        print("No local SECURITY.md file")
        return security_md.Security("")

    try:
        security_file = gh.github.rest.repos.get_content(
            owner=gh.owner,
            repo=gh.repository,
            path="SECURITY.md",
        ).parsed_data
        print("Using SECURITY.md file from the default branch")
        assert isinstance(security_file, githubkit.versions.latest.models.ContentFile)
        # Decode content from base64
        content = base64.b64decode(security_file.content).decode("utf-8") if security_file.content else ""
        return security_md.Security(content)
    except githubkit.exception.RequestFailed as exception:
        if exception.response.status_code == 404:
            print("No security file in the repository")
            return security_md.Security("")
        raise


def get_config() -> tag_publish.configuration.Configuration:
    """Get the configuration, with project and auto detections."""
    config: tag_publish.configuration.Configuration = {}
    if Path(".github/publish.yaml").exists():
        schema_data = pkgutil.get_data("tag_publish", "schema.json")
        assert schema_data is not None
        schema = json.loads(schema_data)

        with Path(".github/publish.yaml").open(encoding="utf-8") as open_file:
            yaml_ = ruamel.yaml.YAML()
            config = yaml_.load(open_file)
            jsonschema_validator.validate(".github/publish.yaml", cast("dict[str, Any]", config), schema)

    return config


def get_value(matched: Optional[Match[str]], config: Optional[VersionTransform], value: str) -> str:
    """
    Get the final value.

    `match`, `config` and `value` are the result of `match`.

    The `config` should have a `to` key with an expand template.

    Arguments:
        matched: The matched object to a regular expression
        config: The result of `compile`
        value: The default value on returned no match

    Return the value

    """
    return matched.expand(config["to"]) if matched is not None and config is not None else value


def compile_re(config: tag_publish.configuration.Transform) -> list[VersionTransform]:
    """
    Compile the from as a regular expression of a dictionary of the config list.

    to be used with convert and match

    Arguments:
        config: The transform config

    Return the compiled transform config.

    """
    result = []
    for conf in config:
        new_conf = cast(
            "VersionTransform",
            {"to": conf.get("to", tag_publish.configuration.TRANSFORM_TO_DEFAULT)},
        )

        from_re = conf.get("from_re", tag_publish.configuration.TRANSFORM_FROM_DEFAULT)
        if from_re[0] != "^":
            from_re = f"^{from_re}"
        if from_re[-1] != "$":
            from_re += "$"

        new_conf["from"] = re.compile(from_re)
        result.append(new_conf)
    return result


def match(
    value: str,
    config: list[VersionTransform],
) -> tuple[Optional[Match[str]], Optional[VersionTransform], str]:
    """
    Get the matched version.

    Arguments:
    ---------
    value: That we want to match with
    config: The result of `compile`

    Returns the re match object, the matched config and the value as a tuple
    On no match it returns None, value

    """
    for conf in config:
        matched = conf["from"].match(value)
        if matched is not None:
            return matched, conf, value
    return None, None, value


@overload
def download_application(application_name: str, binary_filename: Path) -> Path: ...


@overload
def download_application(application_name: str) -> None: ...


def download_application(application_name: str, binary_filename: Optional[Path] = None) -> Optional[Path]:
    """Download the application if necessary, with the included version."""
    binary_full_filename = Path.home() / ".local" / "bin" / binary_filename if binary_filename else None

    if not binary_full_filename.exists() if binary_full_filename else True:
        applications = applications_download.Applications()
        applications.install("helm/chart-releaser")

        versions_data = pkgutil.get_data("tag_publish", "versions.yaml")

        assert versions_data is not None
        versions = yaml.safe_load(versions_data)

        applications.install(
            application_name,
            versions[application_name],
        )

    return binary_full_filename


class PublishedPayload(TypedDict, total=False):
    """The payload to send to the dispatch event."""

    type: str
    image: str
    folder: str
    tag: str
    repository: str
