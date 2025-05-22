#!/usr/bin/env python3

"""The publish script."""

import argparse
import os
import os.path
import re
import subprocess  # nosec
import sys
from pathlib import Path
from re import Match
from typing import Optional, cast

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


def main() -> None:
    """Run the publish."""
    parser = argparse.ArgumentParser(description="Publish the project.")
    parser.add_argument("--group", default="default", help="The publishing group")
    parser.add_argument("--version", help="The version to publish to")
    parser.add_argument(
        "--docker-versions",
        help="The versions to publish on Docker registry, comma separated, ex: 'x,x.y,x.y.z,latest'.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Don't do the publish")
    parser.add_argument("--dry-run-tag", help="Don't do the publish, on a tag")
    parser.add_argument("--dry-run-branch", help="Don't do the publish, on a branch")
    parser.add_argument("--dry-run-pull", help="Don't do the publish, on a pull request")
    parser.add_argument(
        "--type",
        help="The type of version, if no argument provided auto-determinate, can be: "
        "rebuild (in case of rebuild), tag, default_branch, stabilization, feature_branch, pull_request "
        "(for pull request)",
    )
    args = parser.parse_args()

    if args.dry_run_tag is not None:
        args.dry_run = True
        os.environ["GITHUB_REF"] = f"refs/tags/{args.dry_run_tag}"
    if args.dry_run_branch is not None:
        args.dry_run = True
        os.environ["GITHUB_REF"] = f"refs/heads/{args.dry_run_branch}"
    if args.dry_run_pull is not None:
        args.dry_run = True
        os.environ["GITHUB_REF"] = f"refs/pull/{args.dry_run_pull}"

    config = tag_publish.get_config()

    # Describe the kind of release we do: rebuild (specified with --type), tag, default_branch,
    # stabilization_branch, feature_branch, pull_request (merge, number)
    version: str = ""
    ref = os.environ.get("GITHUB_REF", "refs/heads/fake-local")
    local = "GITHUB_REF" not in os.environ

    if args.type is not None and args.version is None:
        print("::error::you specified the argument --type but not the --version")
        sys.exit(1)

    version_type = args.type
    github = tag_publish.GH()
    security = tag_publish.get_security_md(github, local)
    transformers = config.get(
        "transformers",
        cast("tag_publish.configuration.Transformers", tag_publish.configuration.TRANSFORMERS_DEFAULT),
    )

    if args.version is not None:
        version = args.version
    elif ref.startswith("refs/tags/"):
        version_type = "tag"
        tag_match = tag_publish.match(
            ref.split("/", 2)[2],
            tag_publish.compile_re(
                transformers.get("tag_to_version", cast("tag_publish.configuration.Transform", [{}])),
            ),
        )
        version = tag_publish.get_value(*tag_match)
    elif ref.startswith("refs/heads/"):
        branch = ref.split("/", 2)[2]
        if branch == github.default_branch:
            version_type = "default_branch"
        elif branch in security.branches():
            version_type = "stabilization_branch"
        else:
            version_type = "feature_branch"

        if version_type in ("default_branch", "stabilization_branch"):
            branch_match = tag_publish.match(
                ref.split("/", 2)[2],
                tag_publish.compile_re(
                    transformers.get("branch_to_version", cast("tag_publish.configuration.Transform", [{}])),
                ),
            )
            version = tag_publish.get_value(*branch_match)
        else:
            version = branch.replace("/", "_")
    elif ref.startswith("refs/pull/"):
        version_type = "pull_request"
        pull_match = tag_publish.match(
            ref.split("/")[2],
            tag_publish.compile_re(
                transformers.get(
                    "pull_request_to_version",
                    cast("tag_publish.configuration.Transform", [{}]),
                ),
            ),
        )
        version = tag_publish.get_value(*pull_match)
    else:
        print(
            f"WARNING: {ref} is not supported, only ref starting with 'refs/heads/', 'refs/tags/' "
            "or 'refs/pull/' are supported, ignoring",
        )
        sys.exit(0)

    print(f"Create release type {version_type}: {version}" + (" (dry run)" if args.dry_run else ""))

    success = True
    published_payload: list[tag_publish.PublishedPayload] = []

    success &= _handle_pypi_publish(
        args.group,
        args.dry_run,
        config,
        version,
        version_type,
        published_payload,
    )
    success &= _handle_node_publish(
        args.group,
        args.dry_run,
        config,
        version,
        version_type,
        published_payload,
    )
    success &= _handle_docker_publish(
        args.group,
        args.dry_run,
        args.docker_versions,
        config,
        version,
        version_type,
        published_payload,
        security,
    )
    success &= _handle_helm_publish(
        args.group,
        args.dry_run,
        config,
        version,
        version_type,
        github,
        published_payload,
    )
    _trigger_dispatch_events(config, version, version_type, published_payload, github)

    if not success:
        sys.exit(1)


def _handle_pypi_publish(
    group: str,
    dry_run: bool,
    config: tag_publish.configuration.Configuration,
    version: str,
    version_type: str,
    published_payload: list[tag_publish.PublishedPayload],
) -> bool:
    success = True
    pypi_config = config.get("pypi", {})
    if pypi_config:
        if "packages" in pypi_config:
            tag_publish.lib.oidc.pypi_login()

        for package in pypi_config.get("packages", []):
            if package.get("group", tag_publish.configuration.PIP_PACKAGE_GROUP_DEFAULT) == group:
                publish = version_type in pypi_config.get(
                    "versions_type",
                    tag_publish.configuration.PYPI_VERSIONS_DEFAULT,
                )
                folder = package.get("folder", tag_publish.configuration.PYPI_PACKAGE_FOLDER_DEFAULT)
                if dry_run:
                    print(f"{'Publishing' if publish else 'Checking'} '{folder}' to pypi, skipping (dry run)")
                else:
                    success &= tag_publish.publish.pip(package, version, version_type, publish)
                    if publish:
                        published_payload.append({"type": "pypi", "folder": folder})
    return success


def _handle_node_publish(
    group: str,
    dry_run: bool,
    config: tag_publish.configuration.Configuration,
    version: str,
    version_type: str,
    published_payload: list[tag_publish.PublishedPayload],
) -> bool:
    success = True
    node_config = config.get("node", {})
    if node_config:
        if version_type in ("default_branch", "stable_branch"):
            last_tag = (
                subprocess.run(
                    ["git", "describe", "--abbrev=0", "--tags"],
                    check=True,
                    stdout=subprocess.PIPE,
                )
                .stdout.strip()
                .decode()
            )
            commits_number = subprocess.run(
                ["git", "rev-list", "--count", f"{last_tag}..HEAD"],
                check=True,
                stdout=subprocess.PIPE,
            )

            version = f"{last_tag}.{commits_number}"

        for package in node_config.get("packages", []):
            if package.get("group", tag_publish.configuration.NODE_PACKAGE_GROUP_DEFAULT) == group:
                publish = version_type in node_config.get(
                    "versions_type",
                    tag_publish.configuration.NODE_VERSIONS_DEFAULT,
                )
                folder = package.get("folder", tag_publish.configuration.NODE_PACKAGE_FOLDER_DEFAULT)
                for repo_name, repo_config in node_config.get(
                    "repository",
                    cast(
                        "dict[str, tag_publish.configuration.NodeRepository]",
                        tag_publish.configuration.NODE_REPOSITORY_DEFAULT,
                    ),
                ).items():
                    if dry_run:
                        print(
                            f"{'Publishing' if publish else 'Checking'} '{folder}' to {repo_name}, "
                            "skipping (dry run)",
                        )
                    else:
                        success &= tag_publish.publish.node(
                            package,
                            version,
                            version_type,
                            repo_config,
                            publish,
                            node_config.get("args", tag_publish.configuration.NODE_ARGS_DEFAULT),
                        )
                        if publish:
                            published_payload.append({"type": "node", "folder": folder})
    return success


def _handle_docker_publish(
    group: str,
    dry_run: bool,
    docker_versions: str,
    config: tag_publish.configuration.Configuration,
    version: str,
    version_type: str,
    published_payload: list[tag_publish.PublishedPayload],
    security: security_md.Security,
) -> bool:
    success = True
    docker_config = config.get("docker", {})
    if docker_config:
        sys.stdout.flush()
        sys.stderr.flush()
        if docker_config.get("github_oidc_login", tag_publish.configuration.DOCKER_AUTO_LOGIN_DEFAULT):
            subprocess.run(
                [
                    "docker",
                    "login",
                    "ghcr.io",
                    "--username=github",
                    f"--password={os.environ['GITHUB_TOKEN']}",
                ],
                check=True,
            )

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
                if "latest" in row_tags:
                    print("latest found in ", row_tags)
                    add_latest = False
                    break
            if add_latest:
                alt_tags.add("latest")

        images_src: set[str] = set()
        images_full: list[str] = []
        versions = docker_versions.split(",") if docker_versions else [version]
        for image_conf in docker_config.get("images", []):
            if image_conf.get("group", tag_publish.configuration.DOCKER_IMAGE_GROUP_DEFAULT) == group:
                for tag_config in image_conf.get("tags", tag_publish.configuration.DOCKER_IMAGE_TAGS_DEFAULT):
                    tag_src = tag_config.format(version="latest")
                    image_source = f"{image_conf['name']}:{tag_src}"
                    images_src.add(image_source)

                    for name, conf in docker_config.get(
                        "repository",
                        cast(
                            "dict[str, tag_publish.configuration.DockerRepository]",
                            tag_publish.configuration.DOCKER_REPOSITORY_DEFAULT,
                        ),
                    ).items():
                        for docker_version in versions:
                            if version_type in conf.get(
                                "versions_type",
                                tag_publish.configuration.DOCKER_REPOSITORY_VERSIONS_DEFAULT,
                            ):
                                tags = [
                                    tag_config.format(version=alt_tag)
                                    for alt_tag in [docker_version, *alt_tags]
                                ]

                                if dry_run:
                                    for tag in tags:
                                        print(
                                            f"Publishing {image_conf['name']}:{tag} to {name}, skipping "
                                            "(dry run)",
                                        )
                                else:
                                    success &= tag_publish.publish.docker(
                                        conf,
                                        name,
                                        image_conf,
                                        tag_src,
                                        tags,
                                        images_full,
                                        published_payload,
                                    )

        if dry_run:
            sys.exit(0)

        dpkg_versions_path = Path(".github/dpkg-versions.yaml")
        versions_config, dpkg_config_found = tag_publish.lib.docker.get_versions_config()
        dpkg_success = True
        for image in images_src:
            dpkg_success &= tag_publish.lib.docker.check_versions(versions_config.get(image, {}), image)

        if not dpkg_success:
            current_versions_in_images: dict[str, dict[str, str]] = {}
            if dpkg_config_found:
                with dpkg_versions_path.open(encoding="utf-8") as dpkg_versions_file:
                    current_versions_in_images = yaml.load(dpkg_versions_file, Loader=yaml.SafeLoader)
            for image in images_src:
                if image in current_versions_in_images:
                    current_versions_in_images[image] = dict(current_versions_in_images[image])
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
                    "in the image.",
                )
            print("Current versions of the Debian packages in Docker images:")
            print(yaml.dump(current_versions_in_images, Dumper=yaml.SafeDumper, default_flow_style=False))
            if dpkg_config_found:
                with dpkg_versions_path.open("w", encoding="utf-8") as dpkg_versions_file:
                    yaml.dump(
                        current_versions_in_images,
                        dpkg_versions_file,
                        Dumper=yaml.SafeDumper,
                        default_flow_style=False,
                    )

            if dpkg_config_found:
                success = False
    return success


def _handle_helm_publish(
    group: str,
    dry_run: bool,
    config: tag_publish.configuration.Configuration,
    version: str,
    version_type: str,
    github: tag_publish.GH,
    published_payload: list[tag_publish.PublishedPayload],
) -> bool:
    success = True
    helm_config = config.get("helm", {})
    if helm_config.get("packages"):
        tag_publish.download_application("helm/chart-releaser")

        owner = github.owner
        repo = github.repository
        commit_sha = (
            subprocess.run(["git", "rev-parse", "HEAD"], check=True, stdout=subprocess.PIPE)
            .stdout.strip()
            .decode()
        )
        if version_type in ("default_branch", "stabilization_branch"):
            last_tag = (
                subprocess.run(
                    ["git", "describe", "--abbrev=0", "--tags"],
                    check=True,
                    stdout=subprocess.PIPE,
                )
                .stdout.strip()
                .decode()
            )
            commits_number = subprocess.run(
                ["git", "rev-list", "--count", f"{last_tag}..HEAD"],
                check=True,
                stdout=subprocess.PIPE,
            )

            version = f"{last_tag}.{commits_number}"

        for package in helm_config["packages"]:
            if package.get("group", tag_publish.configuration.HELM_PACKAGE_GROUP_DEFAULT) == group:
                versions_type = helm_config.get(
                    "versions_type",
                    tag_publish.configuration.HELM_VERSIONS_DEFAULT,
                )
                publish = version_type in versions_type
                folder = package.get("folder", tag_publish.configuration.HELM_PACKAGE_FOLDER_DEFAULT)
                if publish:
                    if dry_run:
                        print(f"Publishing '{folder}' to helm, skipping (dry run)")
                    else:
                        token = os.environ["GITHUB_TOKEN"]
                        success &= tag_publish.publish.helm(folder, version, owner, repo, commit_sha, token)
                        published_payload.append({"type": "helm", "folder": folder})
                else:
                    print(
                        f"::notice::The folder '{folder}' will be published as helm on version types: "
                        f"{', '.join(versions_type)}",
                    )
    return success


def _trigger_dispatch_events(
    config: tag_publish.configuration.Configuration,
    version: str,
    version_type: str,
    published_payload: list[tag_publish.PublishedPayload],
    github: tag_publish.GH,
) -> None:
    for dispatch_config in config.get("dispatch", []):
        repository = dispatch_config.get("repository")
        event_type = dispatch_config.get("event_type", tag_publish.configuration.DISPATCH_EVENT_TYPE_DEFAULT)

        published = {
            "version": version,
            "version_type": version_type,
            "repository": f"{github.owner}/{github.repository}",
            "items": published_payload,
        }

        if repository:
            print(f"::group::Triggering {event_type} on {repository}")
            owner, repo = repository.split("/", 1)
        else:
            print(f"::group::Triggering {event_type}")
            owner = github.owner
            repo = github.repository
        print(yaml.dump(published, Dumper=yaml.SafeDumper, default_flow_style=False))
        print("::endgroup::")
        github.github.rest.repos.create_dispatch_event(
            owner=owner,
            repo=repo,
            data={"event_type": event_type, "client_payload": {"content": published}},
        )


if __name__ == "__main__":
    main()
