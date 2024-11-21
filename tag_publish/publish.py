"""
The publishing functions.
"""

import datetime
import glob
import json
import os
import re
import subprocess  # nosec
import sys
from typing import Optional

import ruamel
import tomllib

import tag_publish.configuration


def pip(
    package: tag_publish.configuration.PypiPackage,
    version: str,
    version_type: str,
    publish: bool,
    github: tag_publish.GH,
) -> bool:
    """
    Publish to pypi.

    Arguments:
        version: The version that will be published
        version_type: Describe the kind of release we do: rebuild (specified using --type), version_tag,
                    version_branch, feature_branch, feature_tag (for pull request)
        publish: If False only check the package
        package: The package configuration
        github: The GitHub helper

    """
    folder = package.get("folder", tag_publish.configuration.PYPI_PACKAGE_FOLDER_DEFAULT)
    print(f"::group::{'Publishing' if publish else 'Checking'} '{folder}' to pypi")
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        env = {}
        env["VERSION"] = version
        env["VERSION_TYPE"] = version_type
        default_branch = github.repo.default_branch
        is_master = default_branch == version
        env["IS_MASTER"] = "TRUE" if is_master else "FALSE"

        cwd = os.path.abspath(folder)

        dist = os.path.join(cwd, "dist")
        if not os.path.exists(dist):
            os.mkdir(dist)
        if os.path.exists(os.path.join(cwd, "setup.py")):
            cmd = ["python3", "./setup.py", "egg_info", "--no-date"]
            cmd += (
                ["--tag-build=dev" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")]
                if version_type in ("version_branch", "rebuild")
                else []
            )
            cmd.append("bdist_wheel")
        else:
            if not os.path.exists(dist):
                os.mkdir(dist)
            cmd = ["pip", "wheel", "--no-deps", "--wheel-dir=dist", "."]
            if os.path.exists(os.path.join(cwd, "pyproject.toml")):
                use_poetry = False
                if "build_command" not in package:
                    with open(os.path.join(cwd, "pyproject.toml"), "rb") as project_file:
                        pyproject = tomllib.load(project_file)
                    re_splitter = re.compile(r"[<>=]+")
                    for requirement in pyproject.get("build-system", {}).get("requires", []):
                        requirement_split = re_splitter.split(requirement)
                        if requirement_split[0] in ("poetry", "poetry-core"):
                            use_poetry = True
                            break
                    subprocess.run(
                        ["pip", "install", *pyproject.get("build-system", {}).get("requires", [])], check=True
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
        cmd = ["twine"]
        cmd += ["upload", "--verbose", "--disable-progress-bar"] if publish else ["check"]
        cmd += glob.glob(os.path.join(cwd, "dist/*.whl"))
        cmd += glob.glob(os.path.join(cwd, "dist/*.tar.gz"))
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
        version_type: Describe the kind of release we do: rebuild (specified using --type), version_tag,
                    version_branch, feature_branch, feature_tag (for pull request)
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
        if version_type == "version_tag":
            with open(os.path.join(folder, "package.json"), encoding="utf-8") as open_file:
                package_json = json.loads(open_file.read())
            package_json["version"] = version
            with open(os.path.join(folder, "package.json"), "w", encoding="utf-8") as open_file:
                open_file.write(json.dumps(package_json, indent=2) + "\n")

        cwd = os.path.abspath(folder)

        is_github = repo_config["server"] == "npm.pkg.github.com"
        old_npmrc = None
        npmrc_filename = os.path.expanduser("~/.npmrc")
        if is_github:
            old_npmrc = None
            if os.path.exists(npmrc_filename):
                with open(npmrc_filename, encoding="utf-8") as open_file:
                    old_npmrc = open_file.read()
            with open(npmrc_filename, "w", encoding="utf-8") as open_file:
                open_file.write(f"//npm.pkg.github.com/:_authToken={os.environ['GITHUB_TOKEN']}\n")
                open_file.write(f"registry=https://{repo_config['server']}\n")
                open_file.write("always-auth=true\n")

        subprocess.run(["npm", "publish", *([] if publish else ["--dry-run"]), *args], cwd=cwd, check=True)

        if is_github:
            if old_npmrc is None:
                os.remove(npmrc_filename)
            else:
                with open(npmrc_filename, "w", encoding="utf-8") as open_file:
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
        version_type: Describe the kind of release we do: rebuild (specified using --type), version_tag,
                    version_branch, feature_branch, feature_tag (for pull request)
        published: The list of published artifacts to be filled

    """
    print(
        f"::group::Publishing {image_config['name']} to the {name} registry "
        f"using the tags {', '.join(dst_tags)}"
    )
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        new_images_full = []
        if "server" in config:
            for tag in dst_tags:
                subprocess.run(
                    [
                        "docker",
                        "tag",
                        f"{image_config['name']}:{tag_src}",
                        f"{config['server']}/{image_config['name']}:{tag}",
                    ],
                    check=True,
                )
                new_images_full.append(f"{config['server']}/{image_config['name']}:{tag}")
                if published is not None:
                    published.append(
                        {
                            "type": "docker",
                            "repository": config["server"],
                            "image": image_config["name"],
                            "tag": tag,
                        }
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
                            }
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
        with open(os.path.join(folder, "Chart.yaml"), encoding="utf-8") as open_file:
            chart = yaml_.load(open_file)
        chart["version"] = version
        with open(os.path.join(folder, "Chart.yaml"), "w", encoding="utf-8") as open_file:
            yaml_.dump(chart, open_file)
        for index, dependency in enumerate(chart.get("dependencies", [])):
            if dependency["repository"].startswith("https://"):
                subprocess.run(["helm", "repo", "add", str(index), dependency["repository"]], check=True)

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
        if not os.path.exists(".cr-index"):
            os.mkdir(".cr-index")
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
