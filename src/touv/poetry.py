import re
from typing import Any, Iterable, Mapping, MutableMapping
from loguru import logger


def convert_pyproject_toml(data: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a `pyproject.toml` for Poetry to UV.
    """

    poetry = data["tool"]["poetry"]
    if "packages" in poetry:
        logger.warning("Can't handled Poetry [tool.poetry.packages] field yet")

    result = {
        "project": {
            "name": poetry["name"],
            "version": poetry["version"],
            "description": poetry.get("description"),
            "authors": [parse_author(author) for author in poetry["authors"]],
            "readme": poetry["readme"],
            "requires-python": next(
                (convert_version_specifier(v) for k, v in poetry.get("dependencies", {}).items() if k == "python"), None
            ),
        }
    }

    drop_none_values(result)

    return result


def parse_author(author: str) -> dict[str, Any]:
    match = re.match(r"(.*)\s*<(.*)>", author)
    if not match:
        raise ValueError(f"Invalid author: {author!r}")
    return {
        "name": match.group(1),
        "email": match.group(2),
    }


def split_version(v: str) -> tuple[int, ...]:
    return tuple(map(int, v.split(".")))


def join_version(v: Iterable[int]) -> str:
    return ".".join(map(str, v))


def convert_version_specifier(version: str | dict[str, Any]) -> str:
    if isinstance(version, str):
        if version.startswith("^"):
            version_parts = split_version(version[1:])
            next_version_parts = (version_parts[0] + 1, *version_parts[1:])
            return f">={join_version(version_parts)},<{join_version(next_version_parts)}"
        else:
            return version
    else:
        raise ValueError("Not yet supported")


def drop_none_values(data: MutableMapping[str, Any]) -> None:
    for key, value in list(data.items()):
        if value is None:
            del data[key]
        elif isinstance(value, MutableMapping):
            drop_none_values(value)
