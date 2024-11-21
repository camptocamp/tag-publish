"""
Automatically generated file from a JSON schema.
"""

from typing import Any, Dict, List, TypedDict


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

    node: "Node"
    """
    node.

    Configuration to publish on node
    """

    helm: "Helm"
    """
    helm.

    Configuration to publish Helm charts on GitHub release
    """

    dispatch: List["DispatchConfig"]
    """
    Dispatch.

    default:
      []
    """


DISPATCH_CONFIG_DEFAULT: Dict[str, Any] = {}
""" Default value of the field path 'Dispatch item' """


DISPATCH_DEFAULT: List[Any] = []
""" Default value of the field path 'configuration dispatch' """


DISPATCH_EVENT_TYPE_DEFAULT = "published"
""" Default value of the field path 'dispatch config event-type' """


DISPATCH_REPOSITORY_DEFAULT = "camptocamp/argocd-gs-gmf-apps"
""" Default value of the field path 'dispatch config repository' """


DOCKER_AUTO_LOGIN_DEFAULT = False
""" Default value of the field path 'Docker auto_login' """


DOCKER_IMAGE_GROUP_DEFAULT = "default"
""" Default value of the field path 'Docker image group' """


DOCKER_IMAGE_TAGS_DEFAULT = ["{version}"]
""" Default value of the field path 'Docker image tags' """


DOCKER_LATEST_DEFAULT = True
""" Default value of the field path 'Docker latest' """


DOCKER_REPOSITORY_DEFAULT = {
    "github": {"server": "ghcr.io", "versions": ["version_tag", "version_branch", "rebuild"]}
}
""" Default value of the field path 'Docker repository' """


DOCKER_REPOSITORY_VERSIONS_DEFAULT = ["version_tag", "version_branch", "rebuild", "feature_branch"]
""" Default value of the field path 'Docker repository versions' """


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
      github:
        server: ghcr.io
        versions:
        - version_tag
        - version_branch
        - rebuild
    """

    auto_login: bool
    """
    Docker auto login.

    Auto login to the GitHub Docker registry

    default: False
    """


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


HELM_PACKAGE_FOLDER_DEFAULT = "."
""" Default value of the field path 'helm package folder' """


HELM_PACKAGE_GROUP_DEFAULT = "default"
""" Default value of the field path 'helm package group' """


HELM_VERSIONS_DEFAULT = ["version_tag"]
""" Default value of the field path 'helm versions' """


class Helm(TypedDict, total=False):
    """
    helm.

    Configuration to publish Helm charts on GitHub release
    """

    packages: List["HelmPackage"]
    """ The configuration of packages that will be published """

    versions: List[str]
    """
    helm versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - version_tag
    """


class HelmPackage(TypedDict, total=False):
    """
    helm package.

    The configuration of package that will be published
    """

    group: str
    """
    helm package group.

    The image is in the group, should be used with the --group option of tag-publish script

    default: default
    """

    folder: str
    """
    helm package folder.

    The folder of the pypi package

    default: .
    """


NODE_ARGS_DEFAULT = ["--provenance"]
""" Default value of the field path 'node args' """


NODE_PACKAGE_FOLDER_DEFAULT = "."
""" Default value of the field path 'node package folder' """


NODE_PACKAGE_GROUP_DEFAULT = "default"
""" Default value of the field path 'node package group' """


NODE_REPOSITORY_DEFAULT = {"github": {"server": "npm.pkg.github.com"}}
""" Default value of the field path 'node repository' """


NODE_VERSIONS_DEFAULT = ["version_tag"]
""" Default value of the field path 'node versions' """


class Node(TypedDict, total=False):
    """
    node.

    Configuration to publish on node
    """

    packages: List["NodePackage"]
    """ The configuration of packages that will be published """

    versions: List[str]
    """
    node versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - version_tag
    """

    repository: Dict[str, "NodeRepository"]
    """
    Node repository.

    The packages repository where we should publish the packages

    default:
      github:
        server: npm.pkg.github.com
    """

    args: List[str]
    """
    Node args.

    The arguments to pass to the publish command

    default:
      - --provenance
    """


class NodePackage(TypedDict, total=False):
    """
    node package.

    The configuration of package that will be published
    """

    group: str
    """
    node package group.

    The image is in the group, should be used with the --group option of tag-publish script

    default: default
    """

    folder: str
    """
    node package folder.

    The folder of the node package

    default: .
    """


class NodeRepository(TypedDict, total=False):
    """Node repository."""

    server: str
    """ The server URL """


PIP_PACKAGE_GROUP_DEFAULT = "default"
""" Default value of the field path 'pypi package group' """


PYPI_PACKAGE_FOLDER_DEFAULT = "."
""" Default value of the field path 'pypi package folder' """


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

    folder: str
    """
    pypi package folder.

    The folder of the pypi package

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
