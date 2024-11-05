# configuration

_Tag Publish configuration file_

## Properties

- **`version`** _(object)_: The version configurations.
  - **`branch_to_version_re`**: Refer to _[#/definitions/version_transform](#definitions/version_transform)_.
  - **`tag_to_version_re`**: Refer to _[#/definitions/version_transform](#definitions/version_transform)_.
- **`docker`**: Refer to _[#/definitions/publish_docker](#definitions/publish_docker)_.
- **`pypi`**: Refer to _[#/definitions/publish_pypi](#definitions/publish_pypi)_.
- **`helm`**: Refer to _[#/definitions/publish_helm](#definitions/publish_helm)_.

## Definitions

- <a id="definitions/publish_docker"></a>**`publish_docker`**: The configuration used to publish on Docker.
  - **One of**
    - _object_: The configuration used to publish on Docker.
      - **`latest`** _(boolean)_: Publish the latest version on tag latest. Default: `true`.
      - **`images`** _(array)_: List of images to be published.
        - **Items** _(object)_
          - **`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
          - **`name`** _(string)_: The image name.
          - **`tags`** _(array)_: The tag name, will be formatted with the version=<the version>, the image with version=latest should be present when we call the tag-publish script. Default: `["{version}"]`.
            - **Items** _(string)_
      - **`repository`** _(object)_: The repository where we should publish the images. Can contain additional properties. Default: `{"github": {"server": "ghcr.io", "versions": ["version_tag", "version_branch", "rebuild"]}, "dockerhub": {}}`.
        - **Additional properties** _(object)_
          - **`server`** _(string)_: The server URL.
          - **`versions`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script. Default: `["version_tag", "version_branch", "rebuild", "feature_branch"]`.
            - **Items** _(string)_
      - **`dispatch`**: Send a dispatch event to an other repository. Default: `{}`.
        - **One of**
          - _object_: Send a dispatch event to an other repository.
            - **`repository`** _(string)_: The repository name to be triggered. Default: `"camptocamp/argocd-gs-gmf-apps"`.
            - **`event-type`** _(string)_: The event type to be triggered. Default: `"image-update"`.
          - : Must be: `false`.
      - **`snyk`** _(object)_: Checks the published images with Snyk.
        - **`monitor_args`**: The arguments to pass to the Snyk container monitor command. Default: `["--app-vulns"]`.
          - **One of**
            - _array_
              - **Items** _(string)_
            - : Must be: `false`.
        - **`test_args`**: The arguments to pass to the Snyk container test command. Default: `["--app-vulns", "--severity-threshold=critical"]`.
          - **One of**
            - _array_
              - **Items** _(string)_
            - : Must be: `false`.
    - : Must be: `false`.
- <a id="definitions/publish_pypi"></a>**`publish_pypi`**: Configuration to publish on pypi. Default: `{}`.
  - **One of**
    - _object_: Configuration to publish on pypi.
      - **`packages`** _(array)_: The configuration of packages that will be published.
        - **Items** _(object)_: The configuration of package that will be published.
          - **`group`** _(string)_: The image is in the group, should be used with the --group option of tag-publish script. Default: `"default"`.
          - **`path`** _(string)_: The path of the pypi package.
          - **`build_command`** _(array)_: The command used to do the build.
            - **Items** _(string)_
      - **`versions`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script.
        - **Items** _(string)_
    - : Must be: `false`.
- <a id="definitions/publish_helm"></a>**`publish_helm`**: Configuration to publish Helm charts on GitHub release.
  - **One of**
    - _object_: Configuration to publish on Helm charts on GitHub release.
      - **`folders`** _(array)_: The folders that will be published.
        - **Items** _(string)_
      - **`versions`** _(array)_: The kind or version that should be published, tag, branch or value of the --version argument of the tag-publish script.
        - **Items** _(string)_
    - : Must be: `false`.
- <a id="definitions/version_transform"></a>**`version_transform`** _(array)_: A version transformer definition.
  - **Items** _(object)_
    - **`from`** _(string)_: The from regular expression.
    - **`to`** _(string)_: The expand regular expression: https://docs.python.org/3/library/re.html#re.Match.expand.
