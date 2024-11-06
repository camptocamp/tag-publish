#!/usr/bin/env python3

"""
The publish script.
"""

import argparse
import json
import os
import os.path
import random
import re
import subprocess  # nosec
import sys
from re import Match
from typing import Optional, cast

import application_download.cli
import security_md
import yaml

import tag_publish
import tag_publish.configuration
import tag_publish.lib.docker
import tag_publish.lib.oidc
import tag_publish.publish


def match(tpe: str, base_re: str) -> Optional[Match[str]]:
    """
    Return the match for `GITHUB_REF` basically like: `refs/<tpe>/<base_re>`.

    Arguments:
        tpe: The type of ref we want to match (heads, tag, ...)
        base_re: The regular expression to match the value

    """
    if base_re[0] == "^":
        base_re = base_re[1:]
    if base_re[-1] != "$":
        base_re += "$"
    return re.match(f"^refs/{tpe}/{base_re}", os.environ["GITHUB_REF"])


def to_version(full_config: tag_publish.configuration.Configuration, value: str, kind: str) -> str:
    """
    Compute publish version from branch name or tag.

    Arguments:
        full_config: The full configuration
        value: The value to be transformed
        kind: The name of the transformer in the configuration

    """
    item_re = tag_publish.compile_re(
        cast(
            tag_publish.configuration.VersionTransform,
            full_config["version"].get(kind + "_to_version_re", []),
        )
    )
    value_match = tag_publish.match(value, item_re)
    if value_match[0] is not None:
        return tag_publish.get_value(*value_match)
    return value


def main() -> None:
    """
    Run the publish.
    """
    parser = argparse.ArgumentParser(description="Publish the project.")
    parser.add_argument("--group", default="default", help="The publishing group")
    parser.add_argument("--version", help="The version to publish to")
    parser.add_argument(
        "--docker-versions",
        help="The versions to publish on Docker registry, comma separated, ex: 'x,x.y,x.y.z,latest'.",
    )
    parser.add_argument("--snyk-version", help="The version to publish to Snyk")
    parser.add_argument("--branch", help="The branch from which to compute the version")
    parser.add_argument("--tag", help="The tag from which to compute the version")
    parser.add_argument("--dry-run", action="store_true", help="Don't do the publish")
    parser.add_argument(
        "--type",
        help="The type of version, if no argument provided auto-determinate, can be: "
        "rebuild (in case of rebuild), version_tag, version_branch, feature_branch, feature_tag "
        "(for pull request)",
    )
    args = parser.parse_args()

    github = tag_publish.GH()
    config = tag_publish.get_config(github)

    # Describe the kind of release we do: rebuild (specified with --type), version_tag, version_branch,
    # feature_branch, feature_tag (for pull request)
    version: str = ""
    ref = os.environ.get("GITHUB_REF", "refs/heads/fake-local")
    local = "GITHUB_REF" not in os.environ

    if len([e for e in [args.version, args.branch, args.tag] if e is not None]) > 1:
        print("::error::you specified more than one of the arguments --version, --branch or --tag")
        sys.exit(1)

    version_type = args.type

    tag_match = tag_publish.match(
        ref,
        tag_publish.compile_re(config["version"].get("tag_to_version_re", []), "refs/tags/"),
    )
    branch_match = tag_publish.match(
        ref,
        tag_publish.compile_re(config["version"].get("branch_to_version_re", []), "refs/heads/"),
    )
    ref_match = re.match(r"refs/pull/(.*)/merge", ref)

    if args.version is not None:
        version = args.version
    elif args.branch is not None:
        version = to_version(config, args.branch, "branch")
    elif args.tag is not None:
        version = to_version(config, args.tag, "tag")
    elif tag_match[0] is not None:
        if version_type is None:
            version_type = "version_tag"
        else:
            print("::warning::you specified the argument --type but not one of --version, --branch or --tag")
        version = tag_publish.get_value(*tag_match)
    elif branch_match[0] is not None:
        if version_type is None:
            version_type = "version_branch"
        else:
            print("::warning::you specified the argument --type but not one of --version, --branch or --tag")
        version = tag_publish.get_value(*branch_match)
    elif ref_match is not None:
        version = tag_publish.get_value(ref_match, {}, ref)
        if version_type is None:
            version_type = "feature_branch"
    elif ref.startswith("refs/heads/"):
        if version_type is None:
            version_type = "feature_branch"
        else:
            print("::warning::you specified the argument --type but not one of --version, --branch or --tag")
        # By the way we replace '/' by '_' because it isn't supported by Docker
        version = "_".join(ref.split("/")[2:])
    elif ref.startswith("refs/tags/"):
        if version_type is None:
            version_type = "feature_tag"
        else:
            print("::warning::you specified the argument --type but not one of --version, --branch or --tag")
        # By the way we replace '/' by '_' because it isn't supported by Docker
        version = "_".join(ref.split("/")[2:])
    else:
        print(
            f"WARNING: {ref} is not supported, only ref starting with 'refs/heads/' or 'refs/tags/' "
            "are supported, ignoring"
        )
        sys.exit(0)

    if version_type is None:
        print(
            "::error::you specified one of the arguments --version, --branch or --tag but not the --type, "
            f"GitHub ref is: {ref}"
        )
        sys.exit(1)

    if version_type is not None:
        if args.dry_run:
            print(f"Create release type {version_type}: {version} (dry run)")
        else:
            print(f"Create release type {version_type}: {version}")

    github = tag_publish.GH()

    success = True
    published_payload: list[tag_publish.PublishedPayload] = []

    pypi_config = cast(
        tag_publish.configuration.Pypi,
        config.get("pypi", {}) if config.get("pypi", False) else {},
    )
    if pypi_config:
        if pypi_config["packages"]:
            tag_publish.lib.oidc.pypi_login()

        for package in pypi_config["packages"]:
            if package.get("group", tag_publish.configuration.PIP_PACKAGE_GROUP_DEFAULT) == args.group:
                publish = version_type in pypi_config.get(
                    "versions", tag_publish.configuration.PYPI_VERSIONS_DEFAULT
                )
                path = package.get("path", tag_publish.configuration.PYPI_PACKAGE_PATH_DEFAULT)
                if args.dry_run:
                    print(f"{'Publishing' if publish else 'Checking'} '{path}' to pypi, skipping (dry run)")
                else:
                    success &= tag_publish.publish.pip(package, version, version_type, publish, github)
                    published_payload.append(
                        {
                            "type": "pypi",
                            "path": "path",
                            "version": version,
                            "version_type": version_type,
                        }
                    )

    docker_config = cast(
        tag_publish.configuration.Docker,
        config.get("docker", {}) if config.get("docker", False) else {},
    )
    if docker_config:
        security_text = ""
        if local:
            with open("SECURITY.md", encoding="utf-8") as security_file:
                security_text = security_file.read()
                security = security_md.Security(security_text)
        else:
            security = tag_publish.get_security_md(github)

        version_index = security.version_index
        alternate_tag_index = security.alternate_tag_index

        row_index = -1
        if version_index >= 0:
            for index, row in enumerate(security.data):
                if row[version_index] == version:
                    row_index = index
                    break

        alt_tags = set()
        if alternate_tag_index >= 0 and row_index >= 0:
            alt_tags = {
                t.strip() for t in security.data[row_index][alternate_tag_index].split(",") if t.strip()
            }
        if version_index >= 0 and security.data[-1][version_index] == version:
            add_latest = True
            for data in security.data:
                row_tags = {t.strip() for t in data[alternate_tag_index].split(",") if t.strip()}
                print(row_tags)
                if "latest" in row_tags:
                    print("latest found in ", row_tags)
                    add_latest = False
                    break
            if add_latest:
                alt_tags.add("latest")

        images_src: set[str] = set()
        images_full: list[str] = []
        images_snyk: set[str] = set()
        versions = args.docker_versions.split(",") if args.docker_versions else [version]
        for image_conf in docker_config.get("images", []):
            if image_conf.get("group", tag_publish.configuration.DOCKER_IMAGE_GROUP_DEFAULT) == args.group:
                for tag_config in image_conf.get("tags", tag_publish.configuration.DOCKER_IMAGE_TAGS_DEFAULT):
                    tag_src = tag_config.format(version="latest")
                    image_source = f"{image_conf['name']}:{tag_src}"
                    images_src.add(image_source)
                    tag_snyk = tag_config.format(version=args.snyk_version or version).lower()
                    image_snyk = f"{image_conf['name']}:{tag_snyk}"

                    # Workaround sine we have the business plan
                    image_snyk = f"{image_conf['name']}_{tag_snyk}"

                    if not args.dry_run:
                        subprocess.run(["docker", "tag", image_source, image_snyk], check=True)
                    images_snyk.add(image_snyk)
                    if tag_snyk != tag_src and not args.dry_run:
                        subprocess.run(
                            [
                                "docker",
                                "tag",
                                image_source,
                                f"{image_conf['name']}:{tag_snyk}",
                            ],
                            check=True,
                        )

                    for name, conf in {
                        **cast(
                            dict[str, tag_publish.configuration.DockerRepository],
                            tag_publish.configuration.DOCKER_REPOSITORY_DEFAULT,
                        ),
                        **docker_config.get("repository", {}),
                    }.items():
                        for docker_version in versions:
                            if version_type in conf.get(
                                "versions",
                                tag_publish.configuration.DOCKER_REPOSITORY_VERSIONS_DEFAULT,
                            ):
                                tags = [
                                    tag_config.format(version=alt_tag)
                                    for alt_tag in [docker_version, *alt_tags]
                                ]

                                if args.dry_run:
                                    for tag in tags:
                                        print(
                                            f"Publishing {image_conf['name']}:{tag} to {name}, skipping "
                                            "(dry run)"
                                        )
                                else:
                                    success &= tag_publish.publish.docker(
                                        conf,
                                        name,
                                        image_conf,
                                        tag_src,
                                        tags,
                                        images_full,
                                        version_type,
                                        published_payload,
                                    )

        if args.dry_run:
            sys.exit(0)

        snyk_exec, env = tag_publish.snyk_exec()
        for image in images_snyk:
            print(f"::group::Snyk check {image}")
            sys.stdout.flush()
            sys.stderr.flush()
            try:
                if version_type in ("version_branch", "version_tag"):
                    monitor_args = docker_config.get("snyk", {}).get(
                        "monitor_args",
                        tag_publish.configuration.DOCKER_SNYK_MONITOR_ARGS_DEFAULT,
                    )
                    if monitor_args is not False:
                        subprocess.run(  # pylint: disable=subprocess-run-check
                            [
                                snyk_exec,
                                "container",
                                "monitor",
                                *monitor_args,
                                # Available only on the business plan
                                # f"--project-tags=tag={image.split(':')[-1]}",
                                image,
                            ],
                            env=env,
                        )
                test_args = docker_config.get("snyk", {}).get(
                    "test_args", tag_publish.configuration.DOCKER_SNYK_TEST_ARGS_DEFAULT
                )
                snyk_error = False
                if test_args is not False:
                    proc = subprocess.run(
                        [snyk_exec, "container", "test", *test_args, image],
                        check=False,
                        env=env,
                    )
                    if proc.returncode != 0:
                        snyk_error = True
                print("::endgroup::")
                if snyk_error:
                    print("::error::Critical vulnerability found by Snyk in the published image.")
            except subprocess.CalledProcessError as exception:
                print(f"Error: {exception}")
                print("::endgroup::")
                print("::error::With error")

        versions_config, dpkg_config_found = tag_publish.lib.docker.get_versions_config()
        dpkg_success = True
        for image in images_src:
            dpkg_success &= tag_publish.lib.docker.check_versions(versions_config.get(image, {}), image)

        if not dpkg_success:
            current_versions_in_images: dict[str, dict[str, str]] = {}
            if dpkg_config_found:
                with open("ci/dpkg-versions.yaml", encoding="utf-8") as dpkg_versions_file:
                    current_versions_in_images = yaml.load(dpkg_versions_file, Loader=yaml.SafeLoader)
            for image in images_src:
                _, versions_image = tag_publish.lib.docker.get_dpkg_packages_versions(image)
                for dpkg_package, package_version in versions_image.items():
                    if dpkg_package not in current_versions_in_images.get(image, {}):
                        current_versions_in_images.setdefault(image, {})[dpkg_package] = str(package_version)
                for dpkg_package in list(current_versions_in_images[image].keys()):
                    if dpkg_package not in versions_image:
                        del current_versions_in_images[image][dpkg_package]
            if dpkg_config_found:
                print(
                    "::error::Some packages are have a greater version in the config raster then "
                    "in the image."
                )
            print("Current versions of the Debian packages in Docker images:")
            print(yaml.dump(current_versions_in_images, Dumper=yaml.SafeDumper, default_flow_style=False))
            if dpkg_config_found:
                with open("ci/dpkg-versions.yaml", "w", encoding="utf-8") as dpkg_versions_file:
                    yaml.dump(
                        current_versions_in_images,
                        dpkg_versions_file,
                        Dumper=yaml.SafeDumper,
                        default_flow_style=False,
                    )

            if dpkg_config_found:
                success = False

    helm_config = cast(
        tag_publish.configuration.HelmConfig,
        config.get("helm", {}) if config.get("helm", False) else {},
    )
    if (
        helm_config
        and helm_config["folders"]
        and version_type in helm_config.get("versions", tag_publish.configuration.HELM_VERSIONS_DEFAULT)
    ):
        application_download.cli.download_application("helm/chart-releaser")

        owner = github.repo.owner.login
        repo = github.repo.name
        commit_sha = (
            subprocess.run(["git", "rev-parse", "HEAD"], check=True, stdout=subprocess.PIPE)
            .stdout.strip()
            .decode()
        )
        if version_type == "version_branch":
            last_tag = (
                subprocess.run(
                    ["git", "describe", "--abbrev=0", "--tags"], check=True, stdout=subprocess.PIPE
                )
                .stdout.strip()
                .decode()
            )
            expression = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
            while expression.match(last_tag) is None:
                last_tag = (
                    subprocess.run(
                        ["git", "describe", "--abbrev=0", "--tags", f"{last_tag}^"],
                        check=True,
                        stdout=subprocess.PIPE,
                    )
                    .stdout.strip()
                    .decode()
                )

            versions = last_tag.split(".")
            versions[-1] = str(int(versions[-1]) + 1)
            version = ".".join(versions)

        for folder in helm_config["folders"]:
            token = os.environ["GITHUB_TOKEN"]
            success &= tag_publish.publish.helm(folder, version, owner, repo, commit_sha, token)
            published_payload.append(
                {
                    "type": "helm",
                    "path": folder,
                    "version": version,
                    "version_type": version_type,
                }
            )

    config = tag_publish.get_config(tag_publish.GH())

    for published in published_payload:
        for dispatch_config in config.get("dispatch", []):
            repository = dispatch_config.get("repository")
            event_type = dispatch_config.get(
                "event-type", tag_publish.configuration.DISPATCH_EVENT_TYPE_DEFAULT
            )

            id_ = random.randint(1, 100000)  # nosec # noqa: S311
            published["id"] = id_

            if repository:
                print(f"Triggering {event_type}:{id_} on {repository} with {json.dumps(published)}")
                github_repo = github.github.get_repo(repository)
            else:
                print(f"Triggering {event_type}:{id_} with {json.dumps(published)}")
                github_repo = github.repo
            github_repo.create_repository_dispatch(event_type, published)  # type: ignore[arg-type]

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
