"""Typed model for the intranet blueprint.

The blueprint (``site-definition.json``) is a plain dict; these dataclasses give it
structure and validation so the renderer never has to reach into raw dict keys.
Each class has a ``from_dict`` classmethod that parses its slice of the blueprint.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Column:
    """A list/library metadata column."""

    name: str
    type: str = "Text"
    required: bool = False

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Column":
        return cls(
            name=str(d["name"]),
            type=str(d.get("type", "Text")),
            required=bool(d.get("required", False)),
        )


@dataclass
class Library:
    """A document library (or list) with its columns."""

    name: str
    content_type: Optional[str] = None
    retention: Optional[str] = None
    columns: list[Column] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Library":
        return cls(
            name=str(d["name"]),
            content_type=d.get("contentType"),
            retention=d.get("retention"),
            columns=[Column.from_dict(c) for c in d.get("columns", [])],
        )


@dataclass
class FaqEntry:
    """One Q-and-A pair on a FAQ section page."""

    q: str
    a: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "FaqEntry":
        return cls(q=str(d.get("q", "")), a=str(d.get("a", "")))


@dataclass
class Person:
    """One card in a Person Directory section."""

    name: str
    title: str = ""
    email: str = ""
    photo_url: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Person":
        return cls(
            name=str(d.get("name", "")),
            title=str(d.get("title", "")),
            email=str(d.get("email", "")),
            photo_url=str(d.get("photo_url") or d.get("photoUrl") or ""),
        )


@dataclass
class Site:
    """A section site associated to the hub.

    ``type`` selects the renderer: ``"section"`` (default; libraries + links),
    ``"faq"`` (renders ``questions``), or ``"people"`` (renders ``people``).
    """

    key: str
    title: str
    url: str
    template: str = "communication"
    summary: str = ""
    permissions: dict[str, Any] = field(default_factory=dict)
    libraries: list[Library] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    type: str = "section"
    questions: list[FaqEntry] = field(default_factory=list)
    people: list[Person] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Site":
        return cls(
            key=str(d["key"]),
            title=str(d["title"]),
            url=str(d.get("url", "")),
            template=str(d.get("template", "communication")),
            summary=str(d.get("summary", "")),
            permissions=dict(d.get("permissions", {})),
            libraries=[Library.from_dict(l) for l in d.get("libraries", [])],
            links=[str(x) for x in d.get("links", [])],
            type=str(d.get("type", "section")),
            questions=[FaqEntry.from_dict(q) for q in d.get("questions", [])],
            people=[Person.from_dict(p) for p in d.get("people", [])],
        )


@dataclass
class DocLibrary:
    """A Document Center library with sample document rows for the preview."""

    name: str
    columns: list[str] = field(default_factory=list)
    documents: list[dict[str, str]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DocLibrary":
        return cls(
            name=str(d["name"]),
            columns=[str(c) for c in d.get("columns", [])],
            documents=[
                {str(k): str(v) for k, v in row.items()}
                for row in d.get("documents", [])
            ],
        )


@dataclass
class DocumentCenter:
    """The Document Center: a set of metadata-driven libraries."""

    key: str
    title: str
    url: str = ""
    summary: str = ""
    libraries: list[DocLibrary] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DocumentCenter":
        return cls(
            key=str(d.get("key", "document-center")),
            title=str(d.get("title", "Document Center")),
            url=str(d.get("url", "")),
            summary=str(d.get("summary", "")),
            libraries=[DocLibrary.from_dict(l) for l in d.get("libraries", [])],
        )


@dataclass
class NavLink:
    """A global navigation entry pointing at a generated page."""

    label: str
    page: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "NavLink":
        return cls(label=str(d["label"]), page=str(d["page"]))


@dataclass
class NewsItem:
    """A company-news card on the home page."""

    title: str
    date: str = ""
    summary: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "NewsItem":
        return cls(
            title=str(d["title"]),
            date=str(d.get("date", "")),
            summary=str(d.get("summary", "")),
        )


@dataclass
class Intranet:
    """The whole intranet blueprint, parsed and validated."""

    org: str
    tenant: str
    theme: dict[str, Any]
    hub: dict[str, Any]
    nav: list[NavLink]
    sites: list[Site]
    document_center: DocumentCenter
    news: list[NewsItem]
    governance_notes: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Intranet":
        nav_global = d.get("navigation", {}).get("global", [])
        return cls(
            org=str(d.get("org", "Intranet")),
            tenant=str(d.get("tenant", "")),
            theme=dict(d.get("theme", {})),
            hub=dict(d.get("hub", {})),
            nav=[NavLink.from_dict(n) for n in nav_global],
            sites=[Site.from_dict(s) for s in d.get("sites", [])],
            document_center=DocumentCenter.from_dict(d.get("documentCenter", {})),
            news=[NewsItem.from_dict(n) for n in d.get("news", [])],
            governance_notes=dict(d.get("governanceNotes", {})),
        )

    def site_by_key(self, key: str) -> Optional[Site]:
        """Return the section site with ``key``, or ``None``."""
        for s in self.sites:
            if s.key == key:
                return s
        return None
