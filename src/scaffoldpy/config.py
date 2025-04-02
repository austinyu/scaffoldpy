from pydantic import BaseModel


class UserConfig(BaseModel):
    """A configuration for a user."""

    author: str
    author_email: str


ProjectTable = TypedDict(
    "ProjectTable",
    {
        "name": str,
        "version": str,
        "description": str,
        "readme": str,
        "requires-python": str,
        "license": str,
        "license-files": list[str],
        "authors": list[NameContact],
        "maintainers": list[NameContact],
        "keywords": list[str],
        "classifiers": list[str],
        "urls": ProjectUrls,
        "scripts": Any,
        "entry-points": Any,
        "gui-scripts": Any,
        "dependencies": list[str],
        "optional-dependencies": Dependencies,
        "dynamic": list[str],
    },
    total=False,
)
