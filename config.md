# Tag publish configuration

_Tag Publish configuration file (.github/publish.yaml)_

## Properties

- **`transformers`** _(object)_: The version transform configurations. Cannot contain additional properties. Default: `{"pull_request_to_version": [{"to": "pr-\\1"}]}`.
  - **`branch_to_version`**: Refer to _[#/definitions/transform](#definitions/transform)_.
  - **`tag_to_version`**: Refer to _[#/definitions/transform](#definitions/transform)_.
  - **`pull_request_to_version`**: Refer to _[#/definitions/transform](#definitions/transform)_.
- **`docker`**: Refer to _[#/definitions/docker](#definitions/docker)_.
- **`pypi`**: Refer to _[#/definitions/pypi](#definitions/pypi)_.
- **`node`**: Refer to _[#/definitions/node](#definitions/node)_.
- **`helm`**: Refer to _[#/definitions/helm](#definitions/helm)_.
- **`dispatch`** _(array)_: Default: `[]`.
  - **Items** _(object)_: Send a dispatch event to an other repository. Cannot contain additional properties. Default: `{}`.
    - **`repository`** _(string)_: The repository name to be triggered. Default: `"camptocamp/argocd-gs-gmf-apps"`.
    - **`event_type`** _(string)_: The event type to be triggered. Default: `"published"`.

## Definitions

- <a id="definitions/docker"></a>**`docker`** _(object)_: The configuration used to publish on Docker. Cannot contain additional properties.
  - **`latest`** _(boolean)_: Publish the latest version on tag latest. Default: `true`.
  - **`images`** _(array)_: List of images to be published.
    - **Items** _(object)_: Cannot contain additional properties.
      - **`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
      - **`name`** _(string)_: The image name.
      - **`tags`** _(array)_: The tag name, will be formatted with the version=<the version>, the image with version=latest should be present when we call the tag-publish script. Default: `["{version}"]`.
        - **Items** _(string)_
  - **`repository`** _(object)_: The repository where we should publish the images. Can contain additional properties. Default: `{"github": {"host": "ghcr.io", "versions_type": ["tag", "default_branch", "stabilization_branch", "rebuild"]}}`.
    - **Additional properties** _(object)_: Cannot contain additional properties.
      - **`host`** _(string)_: The host of the repository URL.
      - **`versions_type`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["tag", "default_branch", "stabilization_branch", "rebuild", "feature_branch", "pull_request"]`.
        - **Items** _(string)_
  - **`github_oidc_login`** _(boolean)_: Auto login to the GitHub Docker registry. Default: `true`.
- <a id="definitions/pypi"></a>**`pypi`** _(object)_: Configuration to publish on pypi. Cannot contain additional properties.
  - **`packages`** _(array)_: The configuration of packages that will be published.
    - **Items** _(object)_: The configuration of package that will be published. Cannot contain additional properties.
      - **`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
      - **`folder`** _(string)_: The folder of the pypi package. Default: `"."`.
      - **`build_command`** _(array)_: The command used to do the build.
        - **Items** _(string)_
  - **`versions_type`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["tag"]`.
    - **Items** _(string)_
- <a id="definitions/node"></a>**`node`** _(object)_: Configuration to publish on node. Cannot contain additional properties.
  - **`packages`** _(array)_: The configuration of packages that will be published.
    - **Items** _(object)_: The configuration of package that will be published. Cannot contain additional properties.
      - **`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
      - **`folder`** _(string)_: The folder of the node package. Default: `"."`.
  - **`versions_type`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["tag"]`.
    - **Items** _(string)_
  - **`repository`** _(object)_: The packages repository where we should publish the packages. Can contain additional properties. Default: `{"github": {"host": "npm.pkg.github.com"}}`.
    - **Additional properties** _(object)_: Cannot contain additional properties.
      - **`host`** _(string)_: The host of the repository URL.
  - **`args`** _(array)_: The arguments to pass to the publish command. Default: `["--provenance", "--access=public"]`.
    - **Items** _(string)_
- <a id="definitions/helm"></a>**`helm`** _(object)_: Configuration to publish Helm charts on GitHub release. Cannot contain additional properties.
  - **`packages`** _(array)_: The configuration of packages that will be published.
    - **Items** _(object)_: The configuration of package that will be published. Cannot contain additional properties.
      - **`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
      - **`folder`** _(string)_: The folder of the pypi package. Default: `"."`.
  - **`versions_type`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["tag"]`.
    - **Items** _(string)_
- <a id="definitions/transform"></a>**`transform`** _(array)_: A version transformer definition. Default: `[]`.
  - **Items** _(object)_: Cannot contain additional properties.
    - **`from_re`** _(string)_: The from regular expression. Default: `"(.+)"`.
    - **`to`** _(string)_: The expand regular expression: https://docs.python.org/3/library/re.html#re.Match.expand. Default: `"\\1"`.
