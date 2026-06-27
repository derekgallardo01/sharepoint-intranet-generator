"""Tests for the offline intranet generator.

Mirrors the repo's test style: insert the package directory on ``sys.path``, then
import. These assert the blueprint parses and the generator emits the expected
pages with the expected content.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from intranet_gen import generate  # noqa: E402
from intranet_gen.generate import load_intranet  # noqa: E402
from intranet_gen.model import Intranet  # noqa: E402
from intranet_gen.render import render_all  # noqa: E402

HERE = os.path.dirname(__file__)
DEFINITION = os.path.join(HERE, "..", "site-definition.json")


def test_definition_parses_into_intranet():
    net = load_intranet(DEFINITION)
    assert isinstance(net, Intranet)
    assert net.org == "Meridian Advisory"
    # The blueprint defines three section sites, one FAQ, and one people directory.
    keys = {s.key for s in net.sites}
    assert {"hr", "it", "policies", "faq", "people"} <= keys
    assert net.document_center.title == "Document Center"
    assert len(net.document_center.libraries) >= 1


def test_columns_and_libraries_parsed():
    net = load_intranet(DEFINITION)
    policies = net.site_by_key("policies")
    assert policies is not None
    lib = policies.libraries[0]
    assert lib.content_type == "Meridian Policy"
    colnames = {c.name for c in lib.columns}
    assert {"Status", "Review Date", "Owner"} <= colnames
    assert any(c.required for c in lib.columns)


def test_render_all_emits_expected_pages():
    net = load_intranet(DEFINITION)
    pages = render_all(net)
    assert "index.html" in pages
    assert "document-center.html" in pages
    assert "news.html" in pages
    # One page per section site.
    for key in ("hr", "it", "policies"):
        assert f"{key}.html" in pages


def test_home_page_has_title_and_nav():
    net = load_intranet(DEFINITION)
    home = render_all(net)["index.html"]
    assert "Welcome to the Meridian Advisory Intranet" in home
    # Global navigation links to the section pages.
    assert 'href="hr.html"' in home
    assert 'href="document-center.html"' in home


def test_document_center_has_table_and_library_names():
    net = load_intranet(DEFINITION)
    dc = render_all(net)["document-center.html"]
    assert "<table" in dc
    assert "Controlled Policies" in dc
    assert "Contracts" in dc
    # A sample document and its metadata render.
    assert "Code of Conduct" in dc
    assert "Approved" in dc


def test_section_page_has_heading_and_columns():
    net = load_intranet(DEFINITION)
    hr = render_all(net)["hr.html"]
    assert "HR" in hr
    assert "HR Documents" in hr
    assert "Effective Date" in hr


def test_generate_writes_files(tmp_path):
    written = generate(DEFINITION, tmp_path)
    names = {p.name for p in written}
    assert "index.html" in names
    assert "document-center.html" in names
    # Files actually exist and are non-empty HTML documents.
    index = tmp_path / "index.html"
    assert index.exists()
    text = index.read_text(encoding="utf-8")
    assert text.startswith("<!DOCTYPE html>")
    assert len(text) > 200


def test_html_is_escaped(tmp_path):
    # Inject a crafted title; it must be escaped, not rendered as raw HTML.
    with open(DEFINITION, encoding="utf-8") as fh:
        data = json.load(fh)
    data["news"].insert(0, {
        "title": "<script>alert(1)</script>",
        "date": "2026-06-27",
        "summary": "x & y",
    })
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps(data), encoding="utf-8")

    generate(spec, tmp_path / "out")
    home = (tmp_path / "out" / "index.html").read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in home
    assert "&lt;script&gt;" in home
    assert "x &amp; y" in home


def test_output_is_deterministic(tmp_path):
    a = generate(DEFINITION, tmp_path / "a")
    b = generate(DEFINITION, tmp_path / "b")
    assert [p.name for p in a] == [p.name for p in b]
    for pa, pb in zip(a, b):
        assert pa.read_text(encoding="utf-8") == pb.read_text(encoding="utf-8")
