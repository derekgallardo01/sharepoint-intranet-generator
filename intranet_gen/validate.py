"""Structural validation for ``site-definition.json``.

The renderer assumes its input is well-formed; this module is what makes that
assumption hold. :func:`validate` walks a raw blueprint dict (or file) and
returns a list of :class:`ValidationError` — one per issue, each with a dotted
JSON path so a non-engineer can find the line that's wrong.

Empty list = the blueprint is safe to render.

Rules enforced:

- top-level required keys (``org``, ``hub``)
- every navigation entry's ``page`` resolves to a real section, news, faq,
  people, document center, or the home page
- section ``key`` and ``title`` are present, and section keys are unique
- news items have a ``title``
- document-center library references a section that exists (when one is named)
- FAQ pages have at least one well-formed ``{q, a}`` entry
- person-directory entries have a ``name``
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union


@dataclass
class ValidationError:
    """A single problem found in the blueprint.

    ``path`` is a dotted JSON path (``sections[1].nav_label``-style) that points
    at the offending value, ``message`` is a human-readable description, and
    ``severity`` is ``"error"`` (blocks generation by default) or ``"warning"``
    (cosmetic, generation can proceed).
    """

    path: str
    message: str
    severity: str = "error"

    def __str__(self) -> str:
        return f"[{self.severity}] {self.path}: {self.message}"


# ---------- public entry point ----------

DefinitionLike = Union[dict, str, Path]


def validate(definition: DefinitionLike) -> list[ValidationError]:
    """Validate ``definition`` (dict, path-string, or :class:`Path`).

    Returns an empty list when the blueprint is structurally sound. The list is
    in document order so the first error is the first thing to fix.
    """
    data = _load(definition)
    errors: list[ValidationError] = []

    if not isinstance(data, dict):
        return [ValidationError("$", "definition must be a JSON object", "error")]

    _check_top_level(data, errors)
    section_keys = _check_sites(data, errors)
    _check_news(data, errors)
    _check_doc_center(data, errors, section_keys)
    _check_faq_sections(data, errors)
    _check_people_sections(data, errors)
    _check_navigation(data, errors, section_keys)

    return errors


# ---------- loaders ----------

def _load(definition: DefinitionLike) -> Any:
    if isinstance(definition, dict):
        return definition
    path = Path(definition)
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


# ---------- per-section checks ----------

def _check_top_level(d: dict, errors: list[ValidationError]) -> None:
    for key in ("org", "hub"):
        if key not in d:
            errors.append(ValidationError(key, f"missing required key '{key}'", "error"))
    if "tenant" not in d:
        errors.append(ValidationError("tenant", "missing 'tenant' (used in the footer)", "warning"))


def _check_sites(d: dict, errors: list[ValidationError]) -> set[str]:
    seen: set[str] = set()
    sites = d.get("sites", [])
    if not isinstance(sites, list):
        errors.append(ValidationError("sites", "'sites' must be a list", "error"))
        return seen

    for i, site in enumerate(sites):
        base = f"sites[{i}]"
        if not isinstance(site, dict):
            errors.append(ValidationError(base, "site entry must be an object", "error"))
            continue
        key = site.get("key")
        if not key:
            errors.append(ValidationError(f"{base}.key", "section is missing 'key'", "error"))
        else:
            if key in seen:
                errors.append(ValidationError(f"{base}.key", f"duplicate section key '{key}'", "error"))
            seen.add(str(key))
        if not site.get("title"):
            errors.append(ValidationError(f"{base}.title", "section is missing 'title'", "error"))
    return seen


def _check_news(d: dict, errors: list[ValidationError]) -> None:
    news = d.get("news", [])
    if not isinstance(news, list):
        errors.append(ValidationError("news", "'news' must be a list", "error"))
        return
    for i, item in enumerate(news):
        base = f"news[{i}]"
        if not isinstance(item, dict):
            errors.append(ValidationError(base, "news entry must be an object", "error"))
            continue
        if not item.get("title"):
            errors.append(ValidationError(f"{base}.title", "news item is missing 'title'", "error"))


def _check_doc_center(d: dict, errors: list[ValidationError], section_keys: set[str]) -> None:
    dc = d.get("documentCenter")
    if dc is None:
        return
    if not isinstance(dc, dict):
        errors.append(ValidationError("documentCenter", "'documentCenter' must be an object", "error"))
        return

    libs = dc.get("libraries", [])
    if not isinstance(libs, list):
        errors.append(ValidationError("documentCenter.libraries", "must be a list", "error"))
        return

    for i, lib in enumerate(libs):
        base = f"documentCenter.libraries[{i}]"
        if not isinstance(lib, dict):
            errors.append(ValidationError(base, "library entry must be an object", "error"))
            continue
        if not lib.get("name"):
            errors.append(ValidationError(f"{base}.name", "library is missing 'name'", "error"))
        owner = lib.get("ownedBy")
        if owner and owner not in section_keys:
            errors.append(ValidationError(
                f"{base}.ownedBy",
                f"library 'ownedBy' references unknown section '{owner}'",
                "error",
            ))


def _check_faq_sections(d: dict, errors: list[ValidationError]) -> None:
    for i, site in enumerate(d.get("sites", []) or []):
        if not isinstance(site, dict) or site.get("type") != "faq":
            continue
        base = f"sites[{i}]"
        questions = site.get("questions")
        if not isinstance(questions, list) or not questions:
            errors.append(ValidationError(
                f"{base}.questions",
                "faq section must define at least one question",
                "error",
            ))
            continue
        for qi, item in enumerate(questions):
            qbase = f"{base}.questions[{qi}]"
            if not isinstance(item, dict):
                errors.append(ValidationError(qbase, "faq entry must be an object", "error"))
                continue
            if not item.get("q"):
                errors.append(ValidationError(f"{qbase}.q", "faq entry is missing 'q'", "error"))
            if not item.get("a"):
                errors.append(ValidationError(f"{qbase}.a", "faq entry is missing 'a'", "error"))


def _check_people_sections(d: dict, errors: list[ValidationError]) -> None:
    for i, site in enumerate(d.get("sites", []) or []):
        if not isinstance(site, dict) or site.get("type") != "people":
            continue
        base = f"sites[{i}]"
        people = site.get("people")
        if not isinstance(people, list) or not people:
            errors.append(ValidationError(
                f"{base}.people",
                "people section must list at least one person",
                "error",
            ))
            continue
        for pi, person in enumerate(people):
            pbase = f"{base}.people[{pi}]"
            if not isinstance(person, dict):
                errors.append(ValidationError(pbase, "person entry must be an object", "error"))
                continue
            if not person.get("name"):
                errors.append(ValidationError(f"{pbase}.name", "person is missing 'name'", "error"))


def _check_navigation(d: dict, errors: list[ValidationError], section_keys: set[str]) -> None:
    nav = d.get("navigation", {})
    if not isinstance(nav, dict):
        errors.append(ValidationError("navigation", "'navigation' must be an object", "error"))
        return

    items = nav.get("global", [])
    if not isinstance(items, list):
        errors.append(ValidationError("navigation.global", "must be a list", "error"))
        return

    builtin_targets = {"index", "news", "document-center"}
    dc = d.get("documentCenter") or {}
    if isinstance(dc, dict) and dc.get("key"):
        builtin_targets.add(str(dc["key"]))

    for i, link in enumerate(items):
        base = f"navigation.global[{i}]"
        if not isinstance(link, dict):
            errors.append(ValidationError(base, "nav entry must be an object", "error"))
            continue
        if not link.get("label"):
            errors.append(ValidationError(f"{base}.label", "nav entry is missing 'label'", "error"))
        page = link.get("page")
        if not page:
            errors.append(ValidationError(f"{base}.page", "nav entry is missing 'page'", "error"))
            continue
        if page in builtin_targets or page in section_keys:
            continue
        label = link.get("label") or page
        errors.append(ValidationError(
            f"{base}.page",
            f"section '{label}' is referenced in nav but not defined (page='{page}')",
            "error",
        ))
