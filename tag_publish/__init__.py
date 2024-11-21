"""
Tag Publish main module.
"""

import json
import os.path
import pkgutil
import re
import subprocess  # nosec
from re import Match, Pattern
from typing import Any, Optional, TypedDict, cast, overload

import applications_download
import github
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
                ["gh", "auth", "token"], check=True, stdout=subprocess.PIPE, encoding="utf-8"
            ).stdout.strip()
        )
        self.auth = github.Auth.Token(token)
        self.github = github.Github(auth=self.auth)
        self.repo = self.github.get_repo(
            os.environ["GITHUB_REPOSITORY"]
            if "GITHUB_REPOSITORY" in os.environ
            else subprocess.run(
                ["gh", "repo", "view", "--json", "name,owner", "--jq", '(.owner.login + "/" + .name)'],
                check=True,
                stdout=subprocess.PIPE,
                encoding="utf-8",
            ).stdout.strip()
        )
        self.default_branch = self.repo.default_branch


def get_security_md(gh: GH, local: bool) -> security_md.Security:
    """
    Get the SECURITY.md file.

    Arguments:
        gh: The GitHub helper
        local: If we should use the local file

    """
    if local:
        if os.path.exists("SECURITY.md"):
            print("Using the local SECURITY.md file")
            with open("SECURITY.md", encoding="utf-8") as open_file:
                return security_md.Security(open_file.read())
        print("No local SECURITY.md file")
        return security_md.Security("")

    try:
        security_file = gh.repo.get_contents("SECURITY.md")
        assert isinstance(security_file, github.ContentFile.ContentFile)
        print("Using SECURITY.md file from the default branch")
        return security_md.Security(security_file.decoded_content.decode("utf-8"))
    except github.GithubException as exception:
        if exception.status == 404:
            print("No security file in the repository")
            return security_md.Security("")
        else:
            raise exception


def get_config() -> tag_publish.configuration.Configuration:
    """
    Get the configuration, with project and auto detections.
    """
    config: tag_publish.configuration.Configuration = {}
    if os.path.exists(".github/publish.yaml"):
        schema_data = pkgutil.get_data("tag_publish", "schema.json")
        assert schema_data is not None
        schema = json.loads(schema_data)

        with open(".github/publish.yaml", encoding="utf-8") as open_file:
            yaml_ = ruamel.yaml.YAML()
            config = yaml_.load(open_file)
            jsonschema_validator.validate(".github/publish.yaml", cast(dict[str, Any], config), schema)

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
            VersionTransform, {"to": conf.get("to", tag_publish.configuration.TRANSFORM_TO_DEFAULT)}
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
    value: str, config: list[VersionTransform]
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
def download_application(application_name: str, binary_filename: str) -> str: ...


@overload
def download_application(application_name: str) -> None: ...


def download_application(application_name: str, binary_filename: Optional[str] = None) -> Optional[str]:
    """
    Download the application if necessary, with the included version.
    """
    binary_full_filename = (
        os.path.expanduser(os.path.join("~", ".local", "bin", binary_filename)) if binary_filename else None
    )

    if not os.path.exists(binary_full_filename) if binary_full_filename else True:
        applications = applications_download.load_applications(None)
        versions_data = pkgutil.get_data("tag_publish", "versions.yaml")
        assert versions_data is not None
        versions = yaml.safe_load(versions_data)
        applications_download.download_applications(
            applications, {application_name: versions[application_name]}
        )

    return binary_full_filename


class PublishedPayload(TypedDict, total=False):
    """
    The payload to send to the dispatch event.
    """

    type: str
    image: str
    folder: str
    tag: str
    repository: str
