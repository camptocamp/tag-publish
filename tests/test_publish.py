"""Test the publishing functions."""

from pathlib import Path

from tag_publish.publish import check_tag_version, dist_versions, uses_poetry_build


def test_uses_poetry_build_with_poetry_core() -> None:
    assert uses_poetry_build(["poetry-core>=1.0.0", "poetry-dynamic-versioning"])


def test_uses_poetry_build_with_poetry() -> None:
    assert uses_poetry_build(["poetry==2.1.3"])


def test_uses_poetry_build_with_poetry_dynamic_versioning() -> None:
    assert uses_poetry_build(["poetry-dynamic-versioning[plugin]==1.10.1"])


def test_uses_poetry_build_without_poetry() -> None:
    assert not uses_poetry_build(["setuptools>=70.0.0", "wheel"])


def test_uses_poetry_build_with_empty_requires() -> None:
    assert not uses_poetry_build([])


def test_dist_versions_wheel(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "c2c_template-0.0.0-py3-none-any.whl").touch()
    assert dist_versions(tmp_path) == ["0.0.0"]


def test_dist_versions_wheel_and_sdist(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "c2c_template-2.6.1-py3-none-any.whl").touch()
    (dist / "c2c_template-2.6.1.tar.gz").touch()
    assert sorted(dist_versions(tmp_path)) == ["2.6.1", "2.6.1"]


def test_dist_versions_dash_in_name(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "my_package-1.2.3-py3-none-any.whl").touch()
    (dist / "my-package-1.2.3.tar.gz").touch()
    assert sorted(dist_versions(tmp_path)) == ["1.2.3", "1.2.3"]


def test_dist_versions_empty(tmp_path: Path) -> None:
    (tmp_path / "dist").mkdir()
    assert dist_versions(tmp_path) == []


def test_check_tag_version_matching() -> None:
    assert check_tag_version(["2.6.1", "2.6.1"], "2.6.1")


def test_check_tag_version_fallback() -> None:
    assert not check_tag_version(["0.0.0"], "2.6.1")


def test_check_tag_version_no_distribution() -> None:
    assert not check_tag_version([], "2.6.1")


def test_check_tag_version_mixed() -> None:
    assert not check_tag_version(["1.0", "2.0"], "1.0")
