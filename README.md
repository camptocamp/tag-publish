# Tag Publish

## Publishing

The main goals of Tag Publish offer the commands to publish the project,
Using a tag, a stabilization branch, a feature branch or a pull request.

When possible it can do a secret-less publishing (privileged in defaults), if it's not possible the login should be done before the publishing.

See the [documentation](https://github.com/camptocamp/c2cciutils/wiki/Publishing).

## Startup

Set the permissions:

```yaml
permissions:
  # To publish Docker images on GHCR and on npm.pkg.github.com
  packages: write
  # To publish Python packages using OIDC
  id-token: write
  # To publish Helm charts and send repository dispatch notifications
  contents: write
```

Install the package in the worklow:

```yaml
- name: Install tag-publish
  run: pip install tag-publish
```

Do the publishing:

```yaml
- name: Publish
  run: tag-publish
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## New version

To create a new version you should create a Git tag with the version number.

## New stabilization branch

To create a new minor version you just should run `tag-publish-new --version=<version>`.

This will create the stabilization branch and will create a new pull request to update
the `SECURITY.md` file and the Renovate configuration.

This will also create the tags for the backport.

You are welcome to run `tag-publish-new --help` to see what's it's done.

Note that it didn't create a tag, you should do it manually.

To create a patch version you should just create tag.

## Kind of publishing

This tool can publish on different kind of versions:

- `tag`: Related to a Git tag.
- `default_branch`: Related to the default branch.
- `stabilization_branch`: Related to a stabilization branch (including the default branch).
- `feature_branch`: Related to a feature branch or a pull request.

We can also publish on different kind of versions like `rebuild` by using the `--type` argument.

## SECURITY.md

The `SECURITY.md` file should contain the security policy of the repository, especially the end of
support dates.

For compatibility with [`security.md`](https://github.com/sbrunner/security.md/) it should contain an array
with at least the columns `Version` and `Supported Until`. The `Version` column will contain the concerned
version.
The `Supported Until` will contain the date of end of support `dd/mm/yyyy`.
It can also contain the following sentences:

- `Unsupported`: no longer supported => no audit, no rebuild.
- `Best effort`: the support is ended, it is still rebuilt and audited, but this can be stopped without any notice.
- `To be defined`: not yet released or the date will be set related of another project release date (like for GeoMapFish).

See also [GitHub Documentation](https://docs.github.com/en/github/managing-security-vulnerabilities/adding-a-security-policy-to-your-repository)

## Configuration

The configuration file is `.github/publish.yaml`, the schema is `https://raw.githubusercontent.com/camptocamp/tag-publish/<version>/tag_publish/schema.json`.

### Dry run

Dry run publish: `GITHUB_REF=... tag-publish --dry-run ...`

### Python package to pypi repository

Minimum configuration:

```yaml
pypi:
  packages:
    - {}
```

If the file `~/.pypirc` didn't exists we will do a login using OpenId Connect (OIDC), see:
https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-pypi.

By default the package will be published only on tag, if you want to publish on stabilization branch you should add
a `versions` key with the list of versions you want to publish, that can be:
`rebuild` (specified with --type), `tag`, `default_branch`, `stabilization_branch`, `feature_branch`, `pull_request` (for pull request merge: number)

It we have a `setup.py` file, we will be in legacy mode:
When publishing, the version computed from arguments or `GITHUB_REF` is put in environment variable `VERSION`, thus you should use it in `setup.py`, example:

```python
VERSION = os.environ.get("VERSION", "1.0.0")
```

Also we consider that we use `poetry` with [poetry-dynamic-versioning](https://pypi.org/project/poetry-dynamic-versioning/) to manage the version, and [poetry-plugin-tweak-dependencies-version](https://pypi.org/project/poetry-plugin-tweak-dependencies-version/) to manage the dependencies versions.

Example of configuration:

```toml
[tool.poetry-dynamic-versioning]
enable = true
vcs = "git"
pattern = "^(?P<base>\\d+(\\.\\d+)*)"
format-jinja = """
{%- if env.get("VERSION_TYPE") == "default_branch" -%}
{{serialize_pep440(bump_version(base, 1), dev=distance)}}
{%- elif env.get("VERSION_TYPE") == "stabilization_branch" -%}
{{serialize_pep440(bump_version(base, 2), dev=distance)}}
{%- elif distance == 0 -%}
{{serialize_pep440(base)}}
{%- else -%}
{{serialize_pep440(bump_version(base), dev=distance)}}
{%- endif -%}
"""

```

Note that we can access to the environment variables `VERSION`,`VERSION_TYPE`.

Then by default:

- Tag with `1.2.3` => release `1.2.3`
- Commit on feature branch just do a validation
- Commit on `master` branch after the tag 1.3.0 => release `1.4.0.dev1`
- Commit on `1.3` branch after the tag 1.3.0 => release `1.3.1.dev1`

#### Authentication

If the file `~/.pypirc` exists we consider that we ar already logged in also
we will do the login with the `pypi` server with OpenID Connect (OIDC).

The OIDC login is recommended because it didn't needs any additional secrets,
but it need some configuration on pypi in the package,
see the [GitHub Documentation](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-pypi#adding-the-identity-provider-to-pypi).

The required permissions is `id-token: write`.

#### Integration if the package directly in a Docker image

To make it working in the `Dockerfile` you should have in the `poetry` stage:

```Dockerfile
ENV POETRY_DYNAMIC_VERSIONING_BYPASS=dev
RUN poetry export --extras=checks --extras=publish --output=requirements.txt \
    && poetry export --with=dev --output=requirements-dev.txt
```

And in the `run` stage

```Dockerfile
ARG VERSION=dev
RUN --mount=type=cache,target=/root/.cache \
    POETRY_DYNAMIC_VERSIONING_BYPASS=${VERSION} python3 -m pip install --disable-pip-version-check --no-deps --editable=.
```

And in the `Makefile`:

```Makefile
VERSION = $(strip $(shell poetry version --short))

.PHONY: build
build: ## Build the Docker images
    docker build --build-arg=VERSION=$(VERSION) --tag=$(GITHUB_REPOSITORY) .
```

### Docker image to registry

The minimal config is like this:

```yaml
docker:
  images:
    - name: camptocamp/tag-publish
```

If you want to use the GitHub token to be logged in on ghcr you should set `auto_login` to `True`, the
requires the permissions are `packages: write`.

With that the image initially named `camptocamp/tag-publish:latest` will be published on GitHub GHCR and on Docker hub.

The full config is like this:

```yaml
docker:
  github_oidc_login: True
  latest: True
  images:
    - # The base name of the image we want to publish
      name:
  repository:
    <internal_name>:
      # The fqdn name of the server if not Docker hub
      server:
      # List of kinds of versions you want to publish, that can be: rebuild (specified using --type),
      # tag, stabilization_branch, feature_branch, pull_request (for pull request merge: number)
      version:
      # List of tags we want to publish interpreted with `format(version=version)`
      # e.g. if you use `{version}-lite` when you publish the version `1.2.3` the source tag
      # (that should be built by the application build) is `latest-lite`, and it will be published
      # with the tag `1.2.3-lite`.
      tags:
      # If your images are published by different jobs you can separate them in different groups
      # and publish them with `tag-publish --group=<group>`
      group:
```

By default, the last line of the `SECURITY.md` file will be published (`docker`) with the tag
`latest`. Set `latest` to `False` to disable it.

#### Use Renovate to trigger a new build instead of the legacy rebuild

If the `ci/dpkg-versions.yaml` or `.github/dpkg-versions.yaml` file is present, the package list will be updated on publishing.

The versions will be updated by [GHCI](https://github.com/camptocamp/github-app-geo-project/) application.

### Node package to npm repository

Minimum configuration:

```yaml
node:
  packages:
    - {}
```

If the repository server is `npm.pkg.github.com` we will do a login using `GITHUB_TOKEN`.

To publish on `npm.pkg.github.com` you requires the permissions are `packages: write`, and the `id-token: write` for the provenance.

By default the package will be published only on tag.

### HELM

The minimal config is like this:

```yaml
helm:
  packages:
    - {}
```

This will publish the `helm` charts in the current folder using [chart releaser](https://github.com/helm/chart-releaser).

The artifacts will be attached to a GitHub release, and the `index.yaml` file will be updated in the `gh-pages` branch.

The required permission is `contents: write`.

Create the required `gh-pages` branch:

```bash
git checkout --orphan gh-pages
git reset --hard
git commit --allow-empty -m "Initialize gh-pages branch"
git push origin gh-pages
```

## Dispatch

The minimal config is like this:

```yaml
dispatch:
  - {}
```

The required permission is `contents: write`.

This will create a repository dispatch of type `published` on own repository with the `content` e.g.:

```json
{
  "version": "1.2.3",
  "version_type": "tag",
  "repository": "camptocamp/tag-publish",
  "items": [
    {
      "type": "docker",
      "image": "camptocamp/tag-publish",
      "repository": "ghcr.io",
      "tag": "1.2.3"
    },
    {
      "type": "pypi",
      "path": "."
    },
    {
      "type": "helm",
      "path": "."
    }
  ]
}
```

## Contributing

Install the pre-commit hooks:

```bash
pip install pre-commit
pre-commit install --allow-missing-config
```
