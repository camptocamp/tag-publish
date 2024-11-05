#!/usr/bin/env python3

"""
The publish script.
"""

import argparse
import os
import re
import subprocess  # nosec
import sys
from re import Match
from typing import Optional, cast

import requests
import security_md
import yaml

import tag_publish
import tag_publish.configuration
import tag_publish.lib.docker
import tag_publish.lib.oidc
import tag_publish.publish
import tag_publish.scripts.download_applications
from tag_publish.scripts.trigger_image_update import dispatch


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

    config = tag_publish.get_config()

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

    success = True
    pypi_config = cast(
        tag_publish.configuration.PublishPypiConfig,
        config.get("publish", {}).get("pypi", {}) if config.get("publish", {}).get("pypi", False) else {},
    )
    if pypi_config:
        if pypi_config["packages"]:
            tag_publish.lib.oidc.pypi_login()

        for package in pypi_config["packages"]:
            if (
                package.get("group", tag_publish.configuration.PUBLISH_PIP_PACKAGE_GROUP_DEFAULT)
                == args.group
            ):
                publish = version_type in pypi_config.get("versions", [])
                if args.dry_run:
                    print(
                        f"{'Publishing' if publish else 'Checking'} "
                        f"'{package.get('path')}' to pypi, skipping (dry run)"
                    )
                else:
                    success &= tag_publish.publish.pip(package, version, version_type, publish)

    docker_config = cast(
        tag_publish.configuration.PublishDockerConfig,
        config.get("publish", {}).get("docker", {}) if config.get("publish", {}).get("docker", False) else {},
    )
    if docker_config:
        full_repo = tag_publish.get_repository()
        full_repo_split = full_repo.split("/")
        master_branch, _ = tag_publish.get_master_branch(full_repo_split)
        security_text = ""
        if local:
            with open("SECURITY.md", encoding="utf-8") as security_file:
                security_text = security_file.read()
        else:
            security_response = requests.get(
                f"https://raw.githubusercontent.com/{full_repo}/{master_branch}/SECURITY.md",
                headers=tag_publish.add_authorization_header({}),
                timeout=int(os.environ.get("C2CCIUTILS_TIMEOUT", "30")),
            )
            tag_publish.check_response(security_response, False)
            if security_response.ok:
                security_text = security_response.text
            elif security_response.status_code != 404:
                print(f"::error:: {security_response.status_code} {security_response.text}")
                sys.exit(1)

        security = security_md.Security(security_text)
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
            if (
                image_conf.get("group", tag_publish.configuration.PUBLISH_DOCKER_IMAGE_GROUP_DEFAULT)
                == args.group
            ):
                for tag_config in image_conf.get(
                    "tags", tag_publish.configuration.PUBLISH_DOCKER_IMAGE_TAGS_DEFAULT
                ):
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

                    tags_calendar = []
                    for name, conf in {
                        **cast(
                            dict[str, tag_publish.configuration.PublishDockerRepository],
                            tag_publish.configuration.DOCKER_REPOSITORY_DEFAULT,
                        ),
                        **docker_config.get("repository", {}),
                    }.items():
                        for docker_version in versions:
                            tag_dst = tag_config.format(version=docker_version)
                            if tag_dst not in tags_calendar:
                                tags_calendar.append(tag_dst)
                            if version_type in conf.get(
                                "versions",
                                tag_publish.configuration.PUBLISH_DOCKER_REPOSITORY_VERSIONS_DEFAULT,
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
                                        conf, name, image_conf, tag_src, tags, images_full
                                    )

        if args.dry_run:
            sys.exit(0)

        dispatch_config = docker_config.get("dispatch", {})
        if dispatch_config is not False and images_full:
            dispatch(
                dispatch_config.get(
                    "repository", tag_publish.configuration.DOCKER_DISPATCH_REPOSITORY_DEFAULT
                ),
                dispatch_config.get(
                    "event-type", tag_publish.configuration.DOCKER_DISPATCH_EVENT_TYPE_DEFAULT
                ),
                images_full,
            )

        snyk_exec, env = tag_publish.snyk_exec()
        for image in images_snyk:
            print(f"::group::Snyk check {image}")
            sys.stdout.flush()
            sys.stderr.flush()
            try:
                if version_type in ("version_branch", "version_tag"):
                    monitor_args = docker_config.get("snyk", {}).get(
                        "monitor_args",
                        tag_publish.configuration.PUBLISH_DOCKER_SNYK_MONITOR_ARGS_DEFAULT,
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
                    "test_args", tag_publish.configuration.PUBLISH_DOCKER_SNYK_TEST_ARGS_DEFAULT
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
        tag_publish.configuration.PublishHelmConfig,
        config.get("publish", {}).get("helm", {}) if config.get("publish", {}).get("helm", False) else {},
    )
    if helm_config and helm_config["folders"] and version_type in helm_config.get("versions", []):
        tag_publish.scripts.download_applications.download_tag_publish_applications("helm/chart-releaser")

        owner, repo = full_repo_split
        commit_sha = (
            subprocess.run(["git", "rev-parse", "HEAD"], check=True, stdout=subprocess.PIPE)
            .stdout.strip()
            .decode()
        )
        token = (
            os.environ["GITHUB_TOKEN"].strip()
            if "GITHUB_TOKEN" in os.environ
            else tag_publish.gopass("gs/ci/github/token/gopass")
        )
        assert token is not None
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
            success &= tag_publish.publish.helm(folder, version, owner, repo, commit_sha, token)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
