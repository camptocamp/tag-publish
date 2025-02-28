"""The publishing functions."""

import datetime
import json
import os
import re
import subprocess  # nosec
import sys
from pathlib import Path
from typing import Optional

import ruamel
import tomllib

import tag_publish.configuration


def pip(
    package: tag_publish.configuration.PypiPackage,
    version: str,
    version_type: str,
    publish: bool,
) -> bool:
    """
    Publish to pypi.

    Arguments:
        version: The version that will be published
        version_type: Describe the kind of release we do: rebuild (specified using --type), tag,
                    default_branch, stabilization_branch, feature_branch, pull_request (merge, number)
        publish: If False only check the package
        package: The package configuration

    """
    folder = package.get("folder", tag_publish.configuration.PYPI_PACKAGE_FOLDER_DEFAULT)
    print(f"::group::{'Publishing' if publish else 'Checking'} '{folder}' to pypi")
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        env = {}
        env["VERSION"] = version
        env["VERSION_TYPE"] = version_type

        cwd = Path(folder).resolve()

        dist = cwd / "dist"
        if not dist.exists():
            dist.mkdir()
        if (cwd / "setup.py").exists():
            cmd = ["python3", "./setup.py", "egg_info", "--no-date"]
            cmd += (
                ["--tag-build=dev" + datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y%m%d%H%M%S")]
                if version_type in ("default_branch", "stabilization_branch", "rebuild")
                else []
            )
            cmd.append("bdist_wheel")
        else:
            if not dist.exists():
                dist.mkdir()
            cmd = ["pip", "wheel", "--no-deps", "--wheel-dir=dist", "."]
            if (cwd / "pyproject.toml").exists():
                use_poetry = False
                if "build_command" not in package:
                    with (cwd / "pyproject.toml").open("rb") as project_file:
                        pyproject = tomllib.load(project_file)
                    re_splitter = re.compile(r"[<>=]+")
                    for requirement in pyproject.get("build-system", {}).get("requires", []):
                        requirement_split = re_splitter.split(requirement)
                        if requirement_split[0] in ("poetry", "poetry-core"):
                            use_poetry = True
                            break
                    subprocess.run(
                        ["pip", "install", *pyproject.get("build-system", {}).get("requires", [])],
                        check=True,
                    )
                if use_poetry:
                    env_bash = " ".join([f"{key}={value}" for key, value in env.items()])
                    print(f"Run in {cwd}: {env_bash} poetry build")
                    sys.stdout.flush()
                    sys.stderr.flush()
                    subprocess.run(["poetry", "build"], cwd=cwd, env={**os.environ, **env}, check=True)
                    cmd = []
        if cmd:
            cmd = package.get("build_command", cmd)
            subprocess.check_call(cmd, cwd=cwd, env=env)
        cmd = [
            "twine",
            *(["upload", "--verbose", "--disable-progress-bar"] if publish else ["check"]),
            *[str(f) for f in cwd.glob("dist/*.whl")],
            *[str(f) for f in cwd.glob("dist/*.tar.gz")],
        ]
        subprocess.check_call(cmd)
        print("::endgroup::")
    except subprocess.CalledProcessError as exception:
        print(f"Error: {exception}")
        print("::endgroup::")
        print("::error::With error")
        return False
    return True


def node(
    package: tag_publish.configuration.NodePackage,
    version: str,
    version_type: str,
    repo_config: tag_publish.configuration.NodeRepository,
    publish: bool,
    args: list[str],
) -> bool:
    """
    Publish node package to npm.

    Arguments:
        version: The version that will be published
        version_type: Describe the kind of release we do: rebuild (specified using --type), tag,
                    default_branch, stabilization_branch, feature_branch, pull_request (merge, number)
        repo_config: The repository configuration
        publish: If False only check the package
        package: The package configuration
        github: The GitHub helper
        args: The additional arguments to pass to npm publish

    """
    folder = package.get("folder", tag_publish.configuration.PYPI_PACKAGE_FOLDER_DEFAULT)
    print(f"::group::{'Publishing' if publish else 'Checking'} '{folder}' to npm")
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        if version_type == "tag":
            path = Path(folder) / "package.json"
            with path.open(encoding="utf-8") as open_file:
                package_json = json.load(open_file)
            package_json["version"] = version
            with path.open("w", encoding="utf-8") as open_file:
                open_file.write(json.dumps(package_json, indent=2) + "\n")

        cwd = Path(folder).resolve()

        is_github = repo_config["host"] == "npm.pkg.github.com"
        old_npmrc = None
        npmrc_filename = Path("~/.npmrc").expanduser()
        if is_github:
            old_npmrc = None
            if npmrc_filename.exists():
                with npmrc_filename.open(encoding="utf-8") as open_file:
                    old_npmrc = open_file.read()
            with npmrc_filename.open("w", encoding="utf-8") as open_file:
                open_file.write(f"//npm.pkg.github.com/:_authToken={os.environ['GITHUB_TOKEN']}\n")
                open_file.write("always-auth=true\n")

        subprocess.run(["npm", "set", "registry", f"https://{repo_config['host']}"], cwd=cwd, check=True)
        subprocess.run(["npm", "publish", *([] if publish else ["--dry-run"]), *args], cwd=cwd, check=True)

        if is_github:
            if old_npmrc is None:
                npmrc_filename.unlink()
            else:
                with npmrc_filename.open("w", encoding="utf-8") as open_file:
                    open_file.write(old_npmrc)
        print("::endgroup::")
    except subprocess.CalledProcessError as exception:
        print(f"Error: {exception}")
        print("::endgroup::")
        print("::error::With error")
        return False
    return True


def docker(
    config: tag_publish.configuration.DockerRepository,
    name: str,
    image_config: tag_publish.configuration.DockerImage,
    tag_src: str,
    dst_tags: list[str],
    images_full: list[str],
    published: Optional[list[tag_publish.PublishedPayload]] = None,
) -> bool:
    """
    Publish to a Docker registry.

    config is like:
        server: # The server fqdn

    image_config is like:
        name: # The image name

    Arguments:
        config: The publishing config
        name: The repository name, just used to print messages
        image_config: The image config
        tag_src: The source tag (usually latest)
        dst_tags: Publish using the provided tags
        images_full: The list of published images (with tag), used to build the dispatch event
        version_type: Describe the kind of release we do: rebuild (specified using --type), tag,
                    default_branch, stabilization_branch, feature_branch, pull_request (merge, number)
        published: The list of published artifacts to be filled

    """
    print(
        f"::group::Publishing {image_config['name']} to the {name} registry "
        f"using the tags {', '.join(dst_tags)}",
    )
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        new_images_full = []
        if "host" in config:
            for tag in dst_tags:
                subprocess.run(
                    [
                        "docker",
                        "tag",
                        f"{image_config['name']}:{tag_src}",
                        f"{config['host']}/{image_config['name']}:{tag}",
                    ],
                    check=True,
                )
                new_images_full.append(f"{config['host']}/{image_config['name']}:{tag}")
                if published is not None:
                    published.append(
                        {
                            "type": "docker",
                            "repository": config["host"],
                            "image": image_config["name"],
                            "tag": tag,
                        },
                    )
        else:
            for tag in dst_tags:
                if tag_src != tag:
                    subprocess.run(
                        [
                            "docker",
                            "tag",
                            f"{image_config['name']}:{tag_src}",
                            f"{image_config['name']}:{tag}",
                        ],
                        check=True,
                    )
                    if published is not None:
                        published.append(
                            {
                                "type": "docker",
                                "repository": "docker.io",
                                "image": image_config["name"],
                                "tag": tag,
                            },
                        )
                new_images_full.append(f"{image_config['name']}:{tag}")

        for image in new_images_full:
            subprocess.run(["docker", "push", image], check=True)
        images_full += new_images_full

        print("::endgroup::")
    except subprocess.CalledProcessError as exception:
        print(f"Error: {exception}")
        print("::endgroup::")
        print("::error::With error")
        return False
    return True


def helm(folder: str, version: str, owner: str, repo: str, commit_sha: str, token: str) -> bool:
    """
    Publish to pypi.

    Arguments:
        folder: The folder to be published
        version: The version that will be published
        owner: The GitHub repository owner
        repo: The GitHub repository name
        commit_sha: The sha of the current commit
        token: The GitHub token

    """
    print(f"::group::Publishing Helm chart from '{folder}' to GitHub release")
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        yaml_ = ruamel.yaml.YAML()
        with (Path(folder) / "Chart.yaml").open(encoding="utf-8") as open_file:
            chart = yaml_.load(open_file)
        chart["version"] = version
        with (Path(folder) / "Chart.yaml").open("w", encoding="utf-8") as open_file:
            yaml_.dump(chart, open_file)
        for index, dependency in enumerate(chart.get("dependencies", [])):
            if dependency["repository"].startswith("https://"):
                subprocess.run(["helm", "repo", "add", str(index), dependency["repository"]], check=True)

        if subprocess.run(["git", "config", "user.email"], capture_output=True, check=False).returncode != 0:  # pylint: disable=subprocess-run-check
            subprocess.run(["git", "config", "--global", "user.email", "tag-publish@gituhb.com"], check=True)
        if subprocess.run(["git", "config", "user.name"], capture_output=True, check=False).returncode != 0:  # pylint: disable=subprocess-run-check
            subprocess.run(
                ["git", "config", "--global", "user.name", "tag-publish (GitHub Action)"],
                check=True,
            )
        subprocess.run(["cr", "package", folder], check=True)
        subprocess.run(
            [
                "cr",
                "upload",
                f"--owner={owner}",
                f"--git-repo={repo}",
                f"--commit={commit_sha}",
                "--release-name-template={{ .Version }}",
                f"--token={token}",
            ],
            check=True,
        )
        if not Path(".cr-index").exists():
            Path(".cr-index").mkdir()
        subprocess.run(
            [
                "cr",
                "index",
                f"--owner={owner}",
                f"--git-repo={repo}",
                f"--charts-repo=https://{owner}.github.io/{repo}",
                "--push",
                "--release-name-template={{ .Version }}",
                f"--token={token}",
            ],
            check=True,
        )
        print("::endgroup::")
    except subprocess.CalledProcessError as exception:
        print(f"Error: {exception}")
        print("::endgroup::")
        print("::error::With error")
        return False
    return True
