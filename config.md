# Tag publish configuration

_Tag Publish configuration file (.github/publish.yaml)_

## Properties

- **`version`** _(object)_: The version configurations.
  - **`branch_to_version_re`**: Refer to _[#/definitions/version_transform](#definitions/version_transform)_.
  - **`tag_to_version_re`**: Refer to _[#/definitions/version_transform](#definitions/version_transform)_.
- **`docker`**: Refer to _[#/definitions/docker](#definitions/docker)_.
- **`pypi`**: Refer to _[#/definitions/pypi](#definitions/pypi)_.
- **`node`**: Refer to _[#/definitions/node](#definitions/node)_.
- **`helm`**: Refer to _[#/definitions/helm](#definitions/helm)_.
- **`dispatch`** _(array)_: Default: `[]`.
  - **Items** _(object)_: Send a dispatch event to an other repository. Default: `{}`.
    - **`repository`** _(string)_: The repository name to be triggered. Default: `"camptocamp/argocd-gs-gmf-apps"`.
    - **`event-type`** _(string)_: The event type to be triggered. Default: `"published"`.

## Definitions

- <a id="definitions/docker"></a>**`docker`** _(object)_: The configuration used to publish on Docker.
  - **`latest`** _(boolean)_: Publish the latest version on tag latest. Default: `true`.
  - **`images`** _(array)_: List of images to be published.
    - **Items** _(object)_
      - **`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
      - **`name`** _(string)_: The image name.
      - **`tags`** _(array)_: The tag name, will be formatted with the version=<the version>, the image with version=latest should be present when we call the tag-publish script. Default: `["{version}"]`.
        - **Items** _(string)_
  - **`repository`** _(object)_: The repository where we should publish the images. Can contain additional properties. Default: `{"github": {"server": "ghcr.io", "versions": ["version_tag", "version_branch", "rebuild"]}}`.
    - **Additional properties** _(object)_
      - **`server`** _(string)_: The server URL.
      - **`versions`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["version_tag", "version_branch", "rebuild", "feature_branch"]`.
        - **Items** _(string)_
  - **`auto_login`** _(boolean)_: Auto login to the GitHub Docker registry. Default: `false`.
- <a id="definitions/pypi"></a>**`pypi`** _(object)_: Configuration to publish on pypi.
  - **`packages`** _(array)_: The configuration of packages that will be published.
    - **Items** _(object)_: The configuration of package that will be published.
      - **`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
      - **`folder`** _(string)_: The folder of the pypi package. Default: `"."`.
      - **`build_command`** _(array)_: The command used to do the build.
        - **Items** _(string)_
  - **`versions`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["version_tag"]`.
    - **Items** _(string)_
- <a id="definitions/node"></a>**`node`** _(object)_: Configuration to publish on node.
  - **`packages`** _(array)_: The configuration of packages that will be published.
    - **Items** _(object)_: The configuration of package that will be published.
      - **`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
      - **`folder`** _(string)_: The folder of the node package. Default: `"."`.
  - **`versions`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["version_tag"]`.
    - **Items** _(string)_
  - **`repository`** _(object)_: The packages repository where we should publish the packages. Can contain additional properties. Default: `{"github": {"server": "npm.pkg.github.com"}}`.
    - **Additional properties** _(object)_
      - **`server`** _(string)_: The server URL.
  - **`args`** _(array)_: The arguments to pass to the publish command. Default: `["--provenance"]`.
    - **Items** _(string)_
- <a id="definitions/helm"></a>**`helm`** _(object)_: Configuration to publish Helm charts on GitHub release.
  - **`packages`** _(array)_: The configuration of packages that will be published.
    - **Items** _(object)_: The configuration of package that will be published.
      - **`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
      - **`folder`** _(string)_: The folder of the pypi package. Default: `"."`.
  - **`versions`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["version_tag"]`.
    - **Items** _(string)_
- <a id="definitions/version_transform"></a>**`version_transform`** _(array)_: A version transformer definition.
  - **Items** _(object)_
    - **`from`** _(string)_: The from regular expression.
    - **`to`** _(string)_: The expand regular expression: https://docs.python.org/3/library/re.html#re.Match.expand.
