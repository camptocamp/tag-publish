"""
Automatically generated file from a JSON schema.
"""


from typing import Any, TypedDict


class Configuration(TypedDict, total=False):
    r"""
    Tag publish configuration.

    Tag Publish configuration file (.github/publish.yaml)
    """

    transformers: "Transformers"
    r"""
    Transformers.

    The version transform configurations.

    default:
      pull_request_to_version:
      - to: pr-\1
    """

    docker: "Docker"
    r"""
    Docker.

    The configuration used to publish on Docker
    """

    pypi: "Pypi"
    r"""
    pypi.

    Configuration to publish on pypi
    """

    node: "Node"
    r"""
    node.

    Configuration to publish on node
    """

    helm: "Helm"
    r"""
    helm.

    Configuration to publish Helm charts on GitHub release
    """

    dispatch: list["DispatchConfig"]
    r"""
    Dispatch.

    default:
      []
    """



DISPATCH_CONFIG_DEFAULT: dict[str, Any] = {}
r""" Default value of the field path 'Dispatch item' """



DISPATCH_DEFAULT: list[Any] = []
r""" Default value of the field path 'Tag publish configuration dispatch' """



DISPATCH_EVENT_TYPE_DEFAULT = 'published'
r""" Default value of the field path 'dispatch config event_type' """



DISPATCH_REPOSITORY_DEFAULT = 'camptocamp/argocd-gs-gmf-apps'
r""" Default value of the field path 'dispatch config repository' """



DOCKER_AUTO_LOGIN_DEFAULT = True
r""" Default value of the field path 'Docker github_oidc_login' """



DOCKER_IMAGE_GROUP_DEFAULT = 'default'
r""" Default value of the field path 'Docker image group' """



DOCKER_IMAGE_TAGS_DEFAULT = ['{version}']
r""" Default value of the field path 'Docker image tags' """



DOCKER_LATEST_DEFAULT = True
r""" Default value of the field path 'Docker latest' """



DOCKER_REPOSITORY_DEFAULT = {'github': {'host': 'ghcr.io', 'versions_type': ['tag', 'default_branch', 'stabilization_branch', 'rebuild']}}
r""" Default value of the field path 'Docker repository' """



DOCKER_REPOSITORY_VERSIONS_DEFAULT = ['tag', 'default_branch', 'stabilization_branch', 'rebuild', 'feature_branch', 'pull_request']
r""" Default value of the field path 'Docker repository versions_type' """



class DispatchConfig(TypedDict, total=False):
    r"""
    dispatch config.

    Send a dispatch event to an other repository

    default:
      {}
    """

    repository: str
    r"""
    Dispatch repository.

    The repository name to be triggered

    default: camptocamp/argocd-gs-gmf-apps
    """

    event_type: str
    r"""
    Dispatch event type.

    The event type to be triggered

    default: published
    """



class Docker(TypedDict, total=False):
    r"""
    Docker.

    The configuration used to publish on Docker
    """

    latest: bool
    r"""
    Docker latest.

    Publish the latest version on tag latest

    default: True
    """

    images: list["DockerImage"]
    r""" List of images to be published """

    repository: dict[str, "DockerRepository"]
    r"""
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
    r"""
    Docker auto login.

    Auto login to the GitHub Docker registry

    default: True
    """



class DockerImage(TypedDict, total=False):
    r""" Docker image. """

    group: str
    r"""
    Docker image group.

    The image is in the group, should be used with the --group option of tag-publish script

    default: default
    """

    name: str
    r""" The image name """

    tags: list[str]
    r"""
    docker image tags.

    The tag name, will be formatted with the version=<the version>, the image with version=latest should be present when we call the tag-publish script

    default:
      - '{version}'
    """



class DockerRepository(TypedDict, total=False):
    r""" Docker repository. """

    host: str
    r""" The host of the repository URL """

    versions_type: list[str]
    r"""
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
r""" Default value of the field path 'helm package folder' """



HELM_PACKAGE_GROUP_DEFAULT = 'default'
r""" Default value of the field path 'helm package group' """



HELM_VERSIONS_DEFAULT = ['tag']
r""" Default value of the field path 'helm versions_type' """



class Helm(TypedDict, total=False):
    r"""
    helm.

    Configuration to publish Helm charts on GitHub release
    """

    packages: list["HelmPackage"]
    r""" The configuration of packages that will be published """

    versions_type: list[str]
    r"""
    helm versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - tag
    """



class HelmPackage(TypedDict, total=False):
    r"""
    helm package.

    The configuration of package that will be published
    """

    group: str
    r"""
    helm package group.

    The image is in the group, should be used with the --group option of tag-publish script

    default: default
    """

    folder: str
    r"""
    helm package folder.

    The folder of the pypi package

    default: .
    """



NODE_ARGS_DEFAULT = ['--provenance', '--access=public']
r""" Default value of the field path 'node args' """



NODE_PACKAGE_FOLDER_DEFAULT = '.'
r""" Default value of the field path 'node package folder' """



NODE_PACKAGE_GROUP_DEFAULT = 'default'
r""" Default value of the field path 'node package group' """



NODE_REPOSITORY_DEFAULT = {'github': {'host': 'npm.pkg.github.com'}}
r""" Default value of the field path 'node repository' """



NODE_VERSIONS_DEFAULT = ['tag']
r""" Default value of the field path 'node versions_type' """



class Node(TypedDict, total=False):
    r"""
    node.

    Configuration to publish on node
    """

    packages: list["NodePackage"]
    r""" The configuration of packages that will be published """

    versions_type: list[str]
    r"""
    node versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - tag
    """

    repository: dict[str, "NodeRepository"]
    r"""
    Node repository.

    The packages repository where we should publish the packages

    default:
      github:
        host: npm.pkg.github.com
    """

    args: list[str]
    r"""
    Node args.

    The arguments to pass to the publish command

    default:
      - --provenance
      - --access=public
    """



class NodePackage(TypedDict, total=False):
    r"""
    node package.

    The configuration of package that will be published
    """

    group: str
    r"""
    node package group.

    The image is in the group, should be used with the --group option of tag-publish script

    default: default
    """

    folder: str
    r"""
    node package folder.

    The folder of the node package

    default: .
    """



class NodeRepository(TypedDict, total=False):
    r""" Node repository. """

    host: str
    r""" The host of the repository URL """



PIP_PACKAGE_GROUP_DEFAULT = 'default'
r""" Default value of the field path 'pypi package group' """



PYPI_PACKAGE_FOLDER_DEFAULT = '.'
r""" Default value of the field path 'pypi package folder' """



PYPI_VERSIONS_DEFAULT = ['tag']
r""" Default value of the field path 'pypi versions_type' """



class Pypi(TypedDict, total=False):
    r"""
    pypi.

    Configuration to publish on pypi
    """

    packages: list["PypiPackage"]
    r""" The configuration of packages that will be published """

    versions_type: list[str]
    r"""
    pypi versions.

    The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script

    default:
      - tag
    """



class PypiPackage(TypedDict, total=False):
    r"""
    pypi package.

    The configuration of package that will be published
    """

    group: str
    r"""
    pip package group.

    The image is in the group, should be used with the --group option of tag-publish script

    default: default
    """

    folder: str
    r"""
    pypi package folder.

    The folder of the pypi package

    default: .
    """

    build_command: list[str]
    r""" The command used to do the build """



TRANSFORMERS_DEFAULT = {'pull_request_to_version': [{'to': 'pr-\\1'}]}
r""" Default value of the field path 'Tag publish configuration transformers' """



TRANSFORM_DEFAULT: list[Any] = []
r""" Default value of the field path 'transform' """



TRANSFORM_FROM_DEFAULT = '(.+)'
r""" Default value of the field path 'Version transform from_re' """



TRANSFORM_TO_DEFAULT = '\\1'
r""" Default value of the field path 'Version transform to' """



Transform = list["VersionTransform"]
r"""
transform.

A version transformer definition

default:
  []
"""



class Transformers(TypedDict, total=False):
    r"""
    Transformers.

    The version transform configurations.

    default:
      pull_request_to_version:
      - to: pr-\1
    """

    branch_to_version: "Transform"
    r"""
    transform.

    A version transformer definition

    default:
      []
    """

    tag_to_version: "Transform"
    r"""
    transform.

    A version transformer definition

    default:
      []
    """

    pull_request_to_version: "Transform"
    r"""
    transform.

    A version transformer definition

    default:
      []
    """



class VersionTransform(TypedDict, total=False):
    r""" Version transform. """

    from_re: str
    r"""
    transform from.

    The from regular expression

    default: (.+)
    """

    to: str
    r"""
    transform to.

    The expand regular expression: https://docs.python.org/3/library/re.html#re.Match.expand

    default: \1
    """

