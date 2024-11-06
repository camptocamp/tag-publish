"""
Automatically generated file from a JSON schema.
"""

from typing import Any, Dict, List, Literal, TypedDict, Union


class Configuration(TypedDict, total=False):
    """
    configuration.

    Tag Publish configuration file
    """

    version: "Version"
    """
    Version.

    The version configurations
    """

    docker: "Docker"
    """
    Docker.

    The configuration used to publish on Docker
    """

    pypi: "Pypi"
    """
    pypi.

    Configuration to publish on pypi
    """

    helm: "Helm"
    """
    helm.

    Configuration to publish Helm charts on GitHub release

    Aggregation type: oneOf
    Subtype: "HelmConfig"
    """

    dispatch: List["DispatchConfig"]
    """
    Dispatch.

    default:
      - {}
    """


DISPATCH_CONFIG_DEFAULT: Dict[str, Any] = {}
""" Default value of the field path 'Dispatch item' """


DISPATCH_DEFAULT = [{}]
""" Default value of the field path 'configuration dispatch' """


DISPATCH_EVENT_TYPE_DEFAULT = "published"
""" Default value of the field path 'dispatch config event-type' """


DISPATCH_REPOSITORY_DEFAULT = "camptocamp/argocd-gs-gmf-apps"
""" Default value of the field path 'dispatch config repository' """


DOCKER_IMAGE_GROUP_DEFAULT = "default"
""" Default value of the field path 'Docker image group' """


DOCKER_IMAGE_TAGS_DEFAULT = ["{version}"]
""" Default value of the field path 'Docker image tags' """


DOCKER_LATEST_DEFAULT = True
""" Default value of the field path 'Docker latest' """


DOCKER_REPOSITORY_DEFAULT = {
    "github": {"server": "ghcr.io", "versions": ["version_tag", "version_branch", "rebuild"]},
    "dockerhub": {},
}
""" Default value of the field path 'Docker repository' """


DOCKER_REPOSITORY_VERSIONS_DEFAULT = ["version_tag", "version_branch", "rebuild", "feature_branch"]
""" Default value of the field path 'Docker repository versions' """


DOCKER_SNYK_MONITOR_ARGS_DEFAULT = ["--app-vulns"]
""" Default value of the field path 'Docker snyk monitor_args' """


DOCKER_SNYK_TEST_ARGS_DEFAULT = ["--app-vulns", "--severity-threshold=critical"]
""" Default value of the field path 'Docker snyk test_args' """


# | dispatch config.
# |
# | Send a dispatch event to an other repository
# |
# | default:
# |   {}
DispatchConfig = TypedDict(
    "DispatchConfig",
    {
        # | Dispatch repository.
        # |
        # | The repository name to be triggered
        # |
        # | default: camptocamp/argocd-gs-gmf-apps
        "repository": str,
        # | Dispatch event type.
        # |
        # | The event type to be triggered
        # |
        # | default: published
        "event-type": str,
    },
    total=False,
)


class Docker(TypedDict, total=False):
    """
    Docker.

    The configuration used to publish on Docker
    """

    latest: bool
    """
    Docker latest.

    Publish the latest version on tag latest

    default: True
    """

    images: List["DockerImage"]
    """ List of images to be published """

    repository: Dict[str, "DockerRepository"]
    """
    Docker repository.

    The repository where we should publish the images

    default:
      dockerhub: {}
      github:
        server: ghcr.io
        versions:
        - version_tag
        - version_branch
        - rebuild
    """

    snyk: "_DockerSnyk"
    """ Checks the published images with Snyk """


class DockerImage(TypedDict, total=False):
    """Docker image."""

    group: str
    """
    Docker image group.

    The image is in the group, should be used with the --group option of tag-publish script

    default: default
    """

    name: str
    """ The image name """

    tags: List[str]
    """
    docker image tags.

    The tag name, will be formatted with the version=<the version>, the image with version=latest should be present when we call the tag-publish script

    default:
      - '{version}'
    """


class DockerRepository(TypedDict, total=False):
    """Docker repository."""

    server: str
    """ The server URL """

    versions: List[str]
    """
    Docker repository versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - version_tag
      - version_branch
      - rebuild
      - feature_branch
    """


HELM_VERSIONS_DEFAULT = ["version_tag"]
""" Default value of the field path 'helm config versions' """


Helm = Union["HelmConfig", Literal[False]]
"""
helm.

Configuration to publish Helm charts on GitHub release

Aggregation type: oneOf
Subtype: "HelmConfig"
"""


class HelmConfig(TypedDict, total=False):
    """
    helm config.

    Configuration to publish on Helm charts on GitHub release
    """

    folders: List[str]
    """ The folders that will be published """

    versions: List[str]
    """
    helm versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - version_tag
    """


PIP_PACKAGE_GROUP_DEFAULT = "default"
""" Default value of the field path 'pypi package group' """


PYPI_PACKAGE_PATH_DEFAULT = "."
""" Default value of the field path 'pypi package path' """


PYPI_VERSIONS_DEFAULT = ["version_tag"]
""" Default value of the field path 'pypi versions' """


class Pypi(TypedDict, total=False):
    """
    pypi.

    Configuration to publish on pypi
    """

    packages: List["PypiPackage"]
    """ The configuration of packages that will be published """

    versions: List[str]
    """
    pypi versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - version_tag
    """


class PypiPackage(TypedDict, total=False):
    """
    pypi package.

    The configuration of package that will be published
    """

    group: str
    """
    pip package group.

    The image is in the group, should be used with the --group option of tag-publish script

    default: default
    """

    path: str
    """
    pypi package path.

    The path of the pypi package

    default: .
    """

    build_command: List[str]
    """ The command used to do the build """


class Version(TypedDict, total=False):
    """
    Version.

    The version configurations
    """

    branch_to_version_re: "VersionTransform"
    """
    Version transform.

    A version transformer definition
    """

    tag_to_version_re: "VersionTransform"
    """
    Version transform.

    A version transformer definition
    """


VersionTransform = List["_VersionTransformItem"]
"""
Version transform.

A version transformer definition
"""


_DOCKER_SNYK_MONITOR_ARGS_ONEOF0_DEFAULT = ["--app-vulns"]
""" Default value of the field path 'Docker Snyk monitor args oneof0' """


_DOCKER_SNYK_MONITOR_ARGS_ONEOF1_DEFAULT = ["--app-vulns"]
""" Default value of the field path 'Docker Snyk monitor args oneof1' """


_DOCKER_SNYK_TEST_ARGS_ONEOF0_DEFAULT = ["--app-vulns", "--severity-threshold=critical"]
""" Default value of the field path 'Docker Snyk test args oneof0' """


_DOCKER_SNYK_TEST_ARGS_ONEOF1_DEFAULT = ["--app-vulns", "--severity-threshold=critical"]
""" Default value of the field path 'Docker Snyk test args oneof1' """


class _DockerSnyk(TypedDict, total=False):
    """Checks the published images with Snyk"""

    monitor_args: Union["_DockerSnykMonitorArgsOneof0", "_DockerSnykMonitorArgsOneof1"]
    """
    Docker Snyk monitor args.

    The arguments to pass to the Snyk container monitor command

    default:
      - --app-vulns

    Aggregation type: oneOf
    """

    test_args: Union["_DockerSnykTestArgsOneof0", "_DockerSnykTestArgsOneof1"]
    """
    Docker Snyk test args.

    The arguments to pass to the Snyk container test command

    default:
      - --app-vulns
      - --severity-threshold=critical

    Aggregation type: oneOf
    """


_DockerSnykMonitorArgsOneof0 = List[str]
"""
default:
  - --app-vulns
"""


_DockerSnykMonitorArgsOneof1 = Literal[False]
"""
default:
  - --app-vulns
"""


_DockerSnykTestArgsOneof0 = List[str]
"""
default:
  - --app-vulns
  - --severity-threshold=critical
"""


_DockerSnykTestArgsOneof1 = Literal[False]
"""
default:
  - --app-vulns
  - --severity-threshold=critical
"""


_VersionTransformItem = TypedDict(
    "_VersionTransformItem",
    {
        # | The from regular expression
        "from": str,
        # | The expand regular expression: https://docs.python.org/3/library/re.html#re.Match.expand
        "to": str,
    },
    total=False,
)
