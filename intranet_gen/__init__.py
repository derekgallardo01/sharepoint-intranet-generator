"""Offline generator for the SharePoint intranet blueprint.

Reads ``site-definition.json`` and renders a static HTML preview of the proposed
intranet (home page, section pages, and a document-center table) using only the
Python standard library. Lets a client *see* the intranet before any tenant work.
"""

from __future__ import annotations

from .model import Intranet
from .generate import generate

__all__ = ["Intranet", "generate"]
