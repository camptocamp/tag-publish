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

    docker: "PublishDocker"
    """
    Publish Docker.

    The configuration used to publish on Docker

    Aggregation type: oneOf
    Subtype: "PublishDockerConfig"
    """

    pypi: "PublishPypi"
    """
    publish pypi.

    Configuration to publish on pypi

    default:
      {}

    Aggregation type: oneOf
    Subtype: "PublishPypiConfig"
    """

    helm: "PublishHelm"
    """
    publish helm.

    Configuration to publish Helm charts on GitHub release

    Aggregation type: oneOf
    Subtype: "PublishHelmConfig"
    """


DISPATCH_CONFIG_DEFAULT: Dict[str, Any] = {}
""" Default value of the field path 'Publish Docker config dispatch oneof0' """


DOCKER_DISPATCH_EVENT_TYPE_DEFAULT = "image-update"
""" Default value of the field path 'dispatch config event-type' """


DOCKER_DISPATCH_REPOSITORY_DEFAULT = "camptocamp/argocd-gs-gmf-apps"
""" Default value of the field path 'dispatch config repository' """


DOCKER_REPOSITORY_DEFAULT = {
    "github": {"server": "ghcr.io", "versions": ["version_tag", "version_branch", "rebuild"]},
    "dockerhub": {},
}
""" Default value of the field path 'Publish Docker config repository' """


# | dispatch config.
# |
# | Send a dispatch event to an other repository
# |
# | default:
# |   {}
DispatchConfig = TypedDict(
    "DispatchConfig",
    {
        # | Docker dispatch repository.
        # |
        # | The repository name to be triggered
        # |
        # | default: camptocamp/argocd-gs-gmf-apps
        "repository": str,
        # | Docker dispatch event type.
        # |
        # | The event type to be triggered
        # |
        # | default: image-update
        "event-type": str,
    },
    total=False,
)


PUBLISH_DOCKER_IMAGE_GROUP_DEFAULT = "default"
""" Default value of the field path 'Publish Docker image group' """


PUBLISH_DOCKER_IMAGE_TAGS_DEFAULT = ["{version}"]
""" Default value of the field path 'Publish Docker image tags' """


PUBLISH_DOCKER_LATEST_DEFAULT = True
""" Default value of the field path 'Publish Docker config latest' """


PUBLISH_DOCKER_REPOSITORY_VERSIONS_DEFAULT = ["version_tag", "version_branch", "rebuild", "feature_branch"]
""" Default value of the field path 'Publish Docker repository versions' """


PUBLISH_DOCKER_SNYK_MONITOR_ARGS_DEFAULT = ["--app-vulns"]
""" Default value of the field path 'Publish Docker config snyk monitor_args' """


PUBLISH_DOCKER_SNYK_TEST_ARGS_DEFAULT = ["--app-vulns", "--severity-threshold=critical"]
""" Default value of the field path 'Publish Docker config snyk test_args' """


PUBLISH_PIP_PACKAGE_GROUP_DEFAULT = "default"
""" Default value of the field path 'publish pypi package group' """


PUBLISH_PYPI_CONFIG_DEFAULT: Dict[str, Any] = {}
""" Default value of the field path 'publish pypi oneof0' """


PUBLISH_PYPI_DEFAULT: Dict[str, Any] = {}
""" Default value of the field path 'publish_pypi' """


PublishDocker = Union["PublishDockerConfig", Literal[False]]
"""
Publish Docker.

The configuration used to publish on Docker

Aggregation type: oneOf
Subtype: "PublishDockerConfig"
"""


class PublishDockerConfig(TypedDict, total=False):
    """
    Publish Docker config.

    The configuration used to publish on Docker
    """

    latest: bool
    """
    Publish Docker latest.

    Publish the latest version on tag latest

    default: True
    """

    images: List["PublishDockerImage"]
    """ List of images to be published """

    repository: Dict[str, "PublishDockerRepository"]
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

    dispatch: Union["DispatchConfig", "_PublishDockerConfigDispatchOneof1"]
    """
    Send a dispatch event to an other repository

    default:
      {}

    Aggregation type: oneOf
    Subtype: "DispatchConfig"
    """

    snyk: "_PublishDockerConfigSnyk"
    """ Checks the published images with Snyk """


class PublishDockerImage(TypedDict, total=False):
    """Publish Docker image."""

    group: str
    """
    Publish Docker image group.

    The image is in the group, should be used with the --group option of tag-publish script

    default: default
    """

    name: str
    """ The image name """

    tags: List[str]
    """
    publish docker image tags.

    The tag name, will be formatted with the version=<the version>, the image with version=latest should be present when we call the tag-publish script

    default:
      - '{version}'
    """


class PublishDockerRepository(TypedDict, total=False):
    """Publish Docker repository."""

    server: str
    """ The server URL """

    versions: List[str]
    """
    Publish Docker repository versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - version_tag
      - version_branch
      - rebuild
      - feature_branch
    """


PublishHelm = Union["PublishHelmConfig", Literal[False]]
"""
publish helm.

Configuration to publish Helm charts on GitHub release

Aggregation type: oneOf
Subtype: "PublishHelmConfig"
"""


class PublishHelmConfig(TypedDict, total=False):
    """
    publish helm config.

    Configuration to publish on Helm charts on GitHub release
    """

    folders: List[str]
    """ The folders that will be published """

    versions: List[str]
    """ The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script """


PublishPypi = Union["PublishPypiConfig", "_PublishPypiOneof1"]
"""
publish pypi.

Configuration to publish on pypi

default:
  {}

Aggregation type: oneOf
Subtype: "PublishPypiConfig"
"""


class PublishPypiConfig(TypedDict, total=False):
    """
    publish pypi config.

    Configuration to publish on pypi

    default:
      {}
    """

    packages: List["PublishPypiPackage"]
    """ The configuration of packages that will be published """

    versions: List[str]
    """ The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script """


class PublishPypiPackage(TypedDict, total=False):
    """
    publish pypi package.

    The configuration of package that will be published
    """

    group: str
    """
    Publish pip package group.

    The image is in the group, should be used with the --group option of tag-publish script

    default: default
    """

    path: str
    """ The path of the pypi package """

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


_PUBLISH_DOCKER_CONFIG_DISPATCH_DEFAULT: Dict[str, Any] = {}
""" Default value of the field path 'Publish Docker config dispatch' """


_PUBLISH_DOCKER_CONFIG_DISPATCH_ONEOF1_DEFAULT: Dict[str, Any] = {}
""" Default value of the field path 'Publish Docker config dispatch oneof1' """


_PUBLISH_DOCKER_SNYK_MONITOR_ARGS_ONEOF0_DEFAULT = ["--app-vulns"]
""" Default value of the field path 'Publish Docker Snyk monitor args oneof0' """


_PUBLISH_DOCKER_SNYK_MONITOR_ARGS_ONEOF1_DEFAULT = ["--app-vulns"]
""" Default value of the field path 'Publish Docker Snyk monitor args oneof1' """


_PUBLISH_DOCKER_SNYK_TEST_ARGS_ONEOF0_DEFAULT = ["--app-vulns", "--severity-threshold=critical"]
""" Default value of the field path 'Publish Docker Snyk test args oneof0' """


_PUBLISH_DOCKER_SNYK_TEST_ARGS_ONEOF1_DEFAULT = ["--app-vulns", "--severity-threshold=critical"]
""" Default value of the field path 'Publish Docker Snyk test args oneof1' """


_PUBLISH_PYPI_ONEOF1_DEFAULT: Dict[str, Any] = {}
""" Default value of the field path 'publish pypi oneof1' """


_PublishDockerConfigDispatchOneof1 = Literal[False]
"""
default:
  {}
"""


class _PublishDockerConfigSnyk(TypedDict, total=False):
    """Checks the published images with Snyk"""

    monitor_args: Union["_PublishDockerSnykMonitorArgsOneof0", "_PublishDockerSnykMonitorArgsOneof1"]
    """
    Publish Docker Snyk monitor args.

    The arguments to pass to the Snyk container monitor command

    default:
      - --app-vulns

    Aggregation type: oneOf
    """

    test_args: Union["_PublishDockerSnykTestArgsOneof0", "_PublishDockerSnykTestArgsOneof1"]
    """
    Publish Docker Snyk test args.

    The arguments to pass to the Snyk container test command

    default:
      - --app-vulns
      - --severity-threshold=critical

    Aggregation type: oneOf
    """


_PublishDockerSnykMonitorArgsOneof0 = List[str]
"""
default:
  - --app-vulns
"""


_PublishDockerSnykMonitorArgsOneof1 = Literal[False]
"""
default:
  - --app-vulns
"""


_PublishDockerSnykTestArgsOneof0 = List[str]
"""
default:
  - --app-vulns
  - --severity-threshold=critical
"""


_PublishDockerSnykTestArgsOneof1 = Literal[False]
"""
default:
  - --app-vulns
  - --severity-threshold=critical
"""


_PublishPypiOneof1 = Literal[False]
"""
default:
  {}
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
