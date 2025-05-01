# Tag publish configuration

_Tag Publish configuration file (.github/publish.yaml)_

## Properties

- <a id="properties/transformers"></a>**`transformers`** _(object)_: The version transform configurations. Cannot contain additional properties. Default: `{"pull_request_to_version": [{"to": "pr-\\1"}]}`.
  - <a id="properties/transformers/properties/branch_to_version"></a>**`branch_to_version`**: Refer to _[#/definitions/transform](#definitions/transform)_.
  - <a id="properties/transformers/properties/tag_to_version"></a>**`tag_to_version`**: Refer to _[#/definitions/transform](#definitions/transform)_.
  - <a id="properties/transformers/properties/pull_request_to_version"></a>**`pull_request_to_version`**: Refer to _[#/definitions/transform](#definitions/transform)_.
- <a id="properties/docker"></a>**`docker`**: Refer to _[#/definitions/docker](#definitions/docker)_.
- <a id="properties/pypi"></a>**`pypi`**: Refer to _[#/definitions/pypi](#definitions/pypi)_.
- <a id="properties/node"></a>**`node`**: Refer to _[#/definitions/node](#definitions/node)_.
- <a id="properties/helm"></a>**`helm`**: Refer to _[#/definitions/helm](#definitions/helm)_.
- <a id="properties/dispatch"></a>**`dispatch`** _(array)_: Default: `[]`.
  - <a id="properties/dispatch/items"></a>**Items** _(object)_: Send a dispatch event to an other repository. Cannot contain additional properties. Default: `{}`.
    - <a id="properties/dispatch/items/properties/repository"></a>**`repository`** _(string)_: The repository name to be triggered. Default: `"camptocamp/argocd-gs-gmf-apps"`.
    - <a id="properties/dispatch/items/properties/event_type"></a>**`event_type`** _(string)_: The event type to be triggered. Default: `"published"`.

## Definitions

- <a id="definitions/docker"></a>**`docker`** _(object)_: The configuration used to publish on Docker. Cannot contain additional properties.
  - <a id="definitions/docker/properties/latest"></a>**`latest`** _(boolean)_: Publish the latest version on tag latest. Default: `true`.
  - <a id="definitions/docker/properties/images"></a>**`images`** _(array)_: List of images to be published.
    - <a id="definitions/docker/properties/images/items"></a>**Items** _(object)_: Cannot contain additional properties.
      - <a id="definitions/docker/properties/images/items/properties/group"></a>**`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
      - <a id="definitions/docker/properties/images/items/properties/name"></a>**`name`** _(string)_: The image name.
      - <a id="definitions/docker/properties/images/items/properties/tags"></a>**`tags`** _(array)_: The tag name, will be formatted with the version=<the version>, the image with version=latest should be present when we call the tag-publish script. Default: `["{version}"]`.
        - <a id="definitions/docker/properties/images/items/properties/tags/items"></a>**Items** _(string)_
  - <a id="definitions/docker/properties/repository"></a>**`repository`** _(object)_: The repository where we should publish the images. Can contain additional properties. Default: `{"github": {"host": "ghcr.io", "versions_type": ["tag", "default_branch", "stabilization_branch", "rebuild"]}}`.
    - <a id="definitions/docker/properties/repository/additionalProperties"></a>**Additional properties** _(object)_: Cannot contain additional properties.
      - <a id="definitions/docker/properties/repository/additionalProperties/properties/host"></a>**`host`** _(string)_: The host of the repository URL.
      - <a id="definitions/docker/properties/repository/additionalProperties/properties/versions_type"></a>**`versions_type`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["tag", "default_branch", "stabilization_branch", "rebuild", "feature_branch", "pull_request"]`.
        - <a id="definitions/docker/properties/repository/additionalProperties/properties/versions_type/items"></a>**Items** _(string)_
  - <a id="definitions/docker/properties/github_oidc_login"></a>**`github_oidc_login`** _(boolean)_: Auto login to the GitHub Docker registry. Default: `true`.
- <a id="definitions/pypi"></a>**`pypi`** _(object)_: Configuration to publish on pypi. Cannot contain additional properties.
  - <a id="definitions/pypi/properties/packages"></a>**`packages`** _(array)_: The configuration of packages that will be published.
    - <a id="definitions/pypi/properties/packages/items"></a>**Items** _(object)_: The configuration of package that will be published. Cannot contain additional properties.
      - <a id="definitions/pypi/properties/packages/items/properties/group"></a>**`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
      - <a id="definitions/pypi/properties/packages/items/properties/folder"></a>**`folder`** _(string)_: The folder of the pypi package. Default: `"."`.
      - <a id="definitions/pypi/properties/packages/items/properties/build_command"></a>**`build_command`** _(array)_: The command used to do the build.
        - <a id="definitions/pypi/properties/packages/items/properties/build_command/items"></a>**Items** _(string)_
  - <a id="definitions/pypi/properties/versions_type"></a>**`versions_type`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["tag"]`.
    - <a id="definitions/pypi/properties/versions_type/items"></a>**Items** _(string)_
- <a id="definitions/node"></a>**`node`** _(object)_: Configuration to publish on node. Cannot contain additional properties.
  - <a id="definitions/node/properties/packages"></a>**`packages`** _(array)_: The configuration of packages that will be published.
    - <a id="definitions/node/properties/packages/items"></a>**Items** _(object)_: The configuration of package that will be published. Cannot contain additional properties.
      - <a id="definitions/node/properties/packages/items/properties/group"></a>**`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
      - <a id="definitions/node/properties/packages/items/properties/folder"></a>**`folder`** _(string)_: The folder of the node package. Default: `"."`.
  - <a id="definitions/node/properties/versions_type"></a>**`versions_type`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["tag"]`.
    - <a id="definitions/node/properties/versions_type/items"></a>**Items** _(string)_
  - <a id="definitions/node/properties/repository"></a>**`repository`** _(object)_: The packages repository where we should publish the packages. Can contain additional properties. Default: `{"github": {"host": "npm.pkg.github.com"}}`.
    - <a id="definitions/node/properties/repository/additionalProperties"></a>**Additional properties** _(object)_: Cannot contain additional properties.
      - <a id="definitions/node/properties/repository/additionalProperties/properties/host"></a>**`host`** _(string)_: The host of the repository URL.
  - <a id="definitions/node/properties/args"></a>**`args`** _(array)_: The arguments to pass to the publish command. Default: `["--provenance", "--access=public"]`.
    - <a id="definitions/node/properties/args/items"></a>**Items** _(string)_
- <a id="definitions/helm"></a>**`helm`** _(object)_: Configuration to publish Helm charts on GitHub release. Cannot contain additional properties.
  - <a id="definitions/helm/properties/packages"></a>**`packages`** _(array)_: The configuration of packages that will be published.
    - <a id="definitions/helm/properties/packages/items"></a>**Items** _(object)_: The configuration of package that will be published. Cannot contain additional properties.
      - <a id="definitions/helm/properties/packages/items/properties/group"></a>**`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
      - <a id="definitions/helm/properties/packages/items/properties/folder"></a>**`folder`** _(string)_: The folder of the pypi package. Default: `"."`.
  - <a id="definitions/helm/properties/versions_type"></a>**`versions_type`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["tag"]`.
    - <a id="definitions/helm/properties/versions_type/items"></a>**Items** _(string)_
- <a id="definitions/transform"></a>**`transform`** _(array)_: A version transformer definition. Default: `[]`.
  - <a id="definitions/transform/items"></a>**Items** _(object)_: Cannot contain additional properties.
    - <a id="definitions/transform/items/properties/from_re"></a>**`from_re`** _(string)_: The from regular expression. Default: `"(.+)"`.
    - <a id="definitions/transform/items/properties/to"></a>**`to`** _(string)_: The expand regular expression: https://docs.python.org/3/library/re.html#re.Match.expand. Default: `"\\1"`.
