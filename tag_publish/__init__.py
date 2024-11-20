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
import requests
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


def get_security_md(gh: GH) -> security_md.Security:
    """
    Get the SECURITY.md file.

    Arguments:
        gh: The GitHub helper

    """
    try:
        security_file = gh.repo.get_contents("SECURITY.md")
        assert isinstance(security_file, github.ContentFile.ContentFile)
        return security_md.Security(security_file.decoded_content.decode("utf-8"))
    except github.GithubException as exception:
        if exception.status == 404:
            print("No security file in the repository")
            return security_md.Security("")
        else:
            raise exception


def merge(default_config: Any, config: Any) -> Any:
    """
    Deep merge the dictionaries (on dictionaries only, not on arrays).

    Arguments:
        default_config: The default config that will be applied
        config: The base config, will be modified

    """
    if not isinstance(default_config, dict) or not isinstance(config, dict):
        return config

    for key in default_config:
        if key not in config:
            config[key] = default_config[key]
        else:
            merge(default_config[key], config[key])
    return config


def get_config(gh: GH) -> tag_publish.configuration.Configuration:
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

    merge(
        {
            "version": {
                "tag_to_version_re": [
                    {"from": r"([0-9]+.[0-9]+.[0-9]+)", "to": r"\1"},
                ],
                "branch_to_version_re": [
                    {"from": r"([0-9]+.[0-9]+)", "to": r"\1"},
                    {"from": gh.default_branch, "to": gh.default_branch},
                ],
            }
        },
        config,
    )

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
    return matched.expand(config.get("to", r"\1")) if matched is not None and config is not None else value


def compile_re(
    config: tag_publish.configuration.VersionTransform, prefix: str = ""
) -> list[VersionTransform]:
    """
    Compile the from as a regular expression of a dictionary of the config list.

    to be used with convert and match

    Arguments:
        config: The transform config
        prefix: The version prefix

    Return the compiled transform config.

    """
    result = []
    for conf in config:
        new_conf = cast(VersionTransform, dict(conf))

        from_re = conf.get("from", r"(.*)")
        if from_re[0] == "^":
            from_re = from_re[1:]
        if from_re[-1] != "$":
            from_re += "$"
        from_re = f"^{re.escape(prefix)}{from_re}"

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


def does_match(value: str, config: list[VersionTransform]) -> bool:
    """
    Check if the version match with the config patterns.

    Arguments:
    ---------
    value: That we want to match with
    config: The result of `compile`

    Returns True it it does match else False

    """
    matched, _, _ = match(value, config)
    return matched is not None


def check_response(response: requests.Response, raise_for_status: bool = True) -> Any:
    """
    Check the response and raise an exception if it's not ok.

    Also print the X-Ratelimit- headers to get information about the rate limiting.
    """
    for header in response.headers:
        if header.lower().startswith("x-ratelimit-"):
            print(f"{header}: {response.headers[header]}")
    if raise_for_status:
        response.raise_for_status()


def add_authorization_header(headers: dict[str, str]) -> dict[str, str]:
    """
    Add the Authorization header needed to be authenticated on GitHub.

    Arguments:
        headers: The headers

    Return the headers (to be chained)

    """
    try:
        token = os.environ["GITHUB_TOKEN"].strip()
        headers["Authorization"] = f"Bearer {token}"
        return headers
    except FileNotFoundError:
        return headers


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
