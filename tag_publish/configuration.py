"""
Automatically generated file from a JSON schema.
"""


from typing import Any, TypedDict


class Configuration(TypedDict, total=False):
    """
    Tag publish configuration.

    Tag Publish configuration file (.github/publish.yaml)
    """

    transformers: "Transformers"
    """
    Transformers.

    The version transform configurations.

    default:
      pull_request_to_version:
      - to: pr-\1
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

    dispatch: list["DispatchConfig"]
    """
    Dispatch.

    default:
      []
    """



DISPATCH_CONFIG_DEFAULT: dict[str, Any] = {}
""" Default value of the field path 'Dispatch item' """



DISPATCH_DEFAULT: list[Any] = []
""" Default value of the field path 'Tag publish configuration dispatch' """



DISPATCH_EVENT_TYPE_DEFAULT = 'published'
""" Default value of the field path 'dispatch config event_type' """



DISPATCH_REPOSITORY_DEFAULT = 'camptocamp/argocd-gs-gmf-apps'
""" Default value of the field path 'dispatch config repository' """



DOCKER_AUTO_LOGIN_DEFAULT = True
""" Default value of the field path 'Docker github_oidc_login' """



DOCKER_IMAGE_GROUP_DEFAULT = 'default'
""" Default value of the field path 'Docker image group' """



DOCKER_IMAGE_TAGS_DEFAULT = ['{version}']
""" Default value of the field path 'Docker image tags' """



DOCKER_LATEST_DEFAULT = True
""" Default value of the field path 'Docker latest' """



DOCKER_REPOSITORY_DEFAULT = {'github': {'host': 'ghcr.io', 'versions_type': ['tag', 'default_branch', 'stabilization_branch', 'rebuild']}}
""" Default value of the field path 'Docker repository' """



DOCKER_REPOSITORY_VERSIONS_DEFAULT = ['tag', 'default_branch', 'stabilization_branch', 'rebuild', 'feature_branch', 'pull_request']
""" Default value of the field path 'Docker repository versions_type' """



class DispatchConfig(TypedDict, total=False):
    """
    dispatch config.

    Send a dispatch event to an other repository

    default:
      {}
    """

    repository: str
    """
    Dispatch repository.

    The repository name to be triggered

    default: camptocamp/argocd-gs-gmf-apps
    """

    event_type: str
    """
    Dispatch event type.

    The event type to be triggered

    default: published
    """



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

    images: list["DockerImage"]
    """ List of images to be published """

    repository: dict[str, "DockerRepository"]
    """
    Docker repository.

    The repository where we should publish the images

    default:
      github:
        host: ghcr.io
        versions_type:
        - tag
        - default_branch
        - stabilization_branch
        - rebuild
    """

    github_oidc_login: bool
    """
    Docker auto login.

    Auto login to the GitHub Docker registry

    default: True
    """



class DockerImage(TypedDict, total=False):
    """ Docker image. """

    group: str
    """
    Docker image group.

    The image is in the group, should be used with the --group option of tag-publish script

    default: default
    """

    name: str
    """ The image name """

    tags: list[str]
    """
    docker image tags.

    The tag name, will be formatted with the version=<the version>, the image with version=latest should be present when we call the tag-publish script

    default:
      - '{version}'
    """



class DockerRepository(TypedDict, total=False):
    """ Docker repository. """

    host: str
    """ The host of the repository URL """

    versions_type: list[str]
    """
    Docker repository versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - tag
      - default_branch
      - stabilization_branch
      - rebuild
      - feature_branch
      - pull_request
    """



HELM_PACKAGE_FOLDER_DEFAULT = '.'
""" Default value of the field path 'helm package folder' """



HELM_PACKAGE_GROUP_DEFAULT = 'default'
""" Default value of the field path 'helm package group' """



HELM_VERSIONS_DEFAULT = ['tag']
""" Default value of the field path 'helm versions_type' """



class Helm(TypedDict, total=False):
    """
    helm.

    Configuration to publish Helm charts on GitHub release
    """

    packages: list["HelmPackage"]
    """ The configuration of packages that will be published """

    versions_type: list[str]
    """
    helm versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - tag
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



NODE_ARGS_DEFAULT = ['--provenance', '--access=public']
""" Default value of the field path 'node args' """



NODE_PACKAGE_FOLDER_DEFAULT = '.'
""" Default value of the field path 'node package folder' """



NODE_PACKAGE_GROUP_DEFAULT = 'default'
""" Default value of the field path 'node package group' """



NODE_REPOSITORY_DEFAULT = {'github': {'host': 'npm.pkg.github.com'}}
""" Default value of the field path 'node repository' """



NODE_VERSIONS_DEFAULT = ['tag']
""" Default value of the field path 'node versions_type' """



class Node(TypedDict, total=False):
    """
    node.

    Configuration to publish on node
    """

    packages: list["NodePackage"]
    """ The configuration of packages that will be published """

    versions_type: list[str]
    """
    node versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - tag
    """

    repository: dict[str, "NodeRepository"]
    """
    Node repository.

    The packages repository where we should publish the packages

    default:
      github:
        host: npm.pkg.github.com
    """

    args: list[str]
    """
    Node args.

    The arguments to pass to the publish command

    default:
      - --provenance
      - --access=public
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
    """ Node repository. """

    host: str
    """ The host of the repository URL """



PIP_PACKAGE_GROUP_DEFAULT = 'default'
""" Default value of the field path 'pypi package group' """



PYPI_PACKAGE_FOLDER_DEFAULT = '.'
""" Default value of the field path 'pypi package folder' """



PYPI_VERSIONS_DEFAULT = ['tag']
""" Default value of the field path 'pypi versions_type' """



class Pypi(TypedDict, total=False):
    """
    pypi.

    Configuration to publish on pypi
    """

    packages: list["PypiPackage"]
    """ The configuration of packages that will be published """

    versions_type: list[str]
    """
    pypi versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - tag
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

    build_command: list[str]
    """ The command used to do the build """



TRANSFORMERS_DEFAULT = {'pull_request_to_version': [{'to': 'pr-\\1'}]}
""" Default value of the field path 'Tag publish configuration transformers' """



TRANSFORM_DEFAULT: list[Any] = []
""" Default value of the field path 'transform' """



TRANSFORM_FROM_DEFAULT = '(.+)'
""" Default value of the field path 'Version transform from_re' """



TRANSFORM_TO_DEFAULT = '\\1'
""" Default value of the field path 'Version transform to' """



Transform = list["VersionTransform"]
"""
transform.

A version transformer definition

default:
  []
"""



class Transformers(TypedDict, total=False):
    """
    Transformers.

    The version transform configurations.

    default:
      pull_request_to_version:
      - to: pr-\1
    """

    branch_to_version: "Transform"
    """
    transform.

    A version transformer definition

    default:
      []
    """

    tag_to_version: "Transform"
    """
    transform.

    A version transformer definition

    default:
      []
    """

    pull_request_to_version: "Transform"
    """
    transform.

    A version transformer definition

    default:
      []
    """



class VersionTransform(TypedDict, total=False):
    """ Version transform. """

    from_re: str
    """
    transform from.

    The from regular expression

    default: (.+)
    """

    to: str
    """
    transform to.

    The expand regular expression: https://docs.python.org/3/library/re.html#re.Match.expand

    default: \1
    """

