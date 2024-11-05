#!/usr/bin/env python3

"""
Trigger an image update on the argocd repository.
"""

import os.path
import random
import subprocess  # nosec

import requests


def dispatch(repository: str, event_type: str, images_full: list[str]) -> None:
    """
    Trigger an image update on the argocd repository.
    """
    id_ = random.randint(1, 100000)  # nosec # noqa: S311
    print(f"Triggering {event_type}:{id_} on {repository} with {','.join(images_full)}")

    response = requests.post(
        f"https://api.github.com/repos/{repository}/dispatches",
        headers={
            "Content-Type": "application/json2",
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "token "
            + subprocess.run(
                ["gopass", "show", "gs/ci/github/token/gopass"], check=True, stdout=subprocess.PIPE
            )
            .stdout.decode()
            .strip(),
        },
        json={"event_type": event_type, "client_payload": {"name": " ".join(images_full), "id": id_}},
        timeout=int(os.environ.get("C2CCIUTILS_TIMEOUT", "30")),
    )
    response.raise_for_status()
