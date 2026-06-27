import io
import json
import os
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import cli  # noqa: E402
from intranet_gen.generate import load_intranet  # noqa: E402
from intranet_gen.render import render_all  # noqa: E402
from intranet_gen.validate import validate  # noqa: E402

DEFINITION = os.path.join(os.path.dirname(HERE), "site-definition.json")


# --- validation ---------------------------------------------------------------

def test_validation_passes_for_sample_definition():
    errors = [e for e in validate(DEFINITION) if e.severity == "error"]
    assert errors == []


def test_alternate_industry_definition_validates_and_renders():
    alt = os.path.join(os.path.dirname(HERE), "examples",
                       "site-definition-acme-manufacturing.json")
    errors = [e for e in validate(alt) if e.severity == "error"]
    assert errors == [], f"alternate def has errors: {errors[:3]}"
    pages = render_all(load_intranet(alt))
    for key in ("production", "quality", "supply-chain", "engineering",
                "faq", "people"):
        assert f"{key}.html" in pages, f"missing {key}.html in render"
    assert "Plant Manager" in pages["people.html"]
    assert "Incident report" in pages["faq.html"]


def test_validation_catches_missing_org():
    errors = validate({"hub": {"title": "x"}, "tenant": "x"})
    assert any("missing required key 'org'" in e.message for e in errors)


def test_validation_catches_duplicate_section_keys():
    errors = validate({
        "org": "x", "tenant": "x", "hub": {"title": "x"},
        "sites": [{"key": "hr", "title": "HR"}, {"key": "hr", "title": "HR"}],
    })
    assert any("duplicate section key 'hr'" in e.message for e in errors)


def test_validation_catches_nav_to_undefined_section():
    errors = validate({
        "org": "x", "tenant": "x", "hub": {"title": "x"},
        "sites": [{"key": "hr", "title": "HR"}],
        "navigation": {"global": [{"label": "Policies", "page": "policies"}]},
    })
    assert any("referenced in nav but not defined" in e.message for e in errors)


# --- FAQ rendering ------------------------------------------------------------

def test_faq_page_renders_questions_in_accordion():
    net = load_intranet(DEFINITION)
    pages = render_all(net)
    assert "faq.html" in pages
    faq = pages["faq.html"]
    assert "How do I reset my password?" in faq
    assert "<details>" in faq and "<summary>" in faq
    # Answer text appears alongside the question.
    assert "self-service portal" in faq


# --- Person Directory rendering ----------------------------------------------

def test_people_page_renders_each_person():
    net = load_intranet(DEFINITION)
    pages = render_all(net)
    assert "people.html" in pages
    p = pages["people.html"]
    assert "A. Okafor" in p
    assert "Head of People &amp; Culture" in p or "Head of People & Culture" in p
    assert "mailto:r.vasquez@example.com" in p
    assert 'class="person-card"' in p


# --- CLI ----------------------------------------------------------------------

def test_cli_validate_returns_zero_for_valid_definition():
    rc = cli.main(["validate", DEFINITION])
    assert rc == 0


def test_cli_validate_returns_one_for_invalid_definition(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"hub": {"title": "x"}}), encoding="utf-8")
    out = io.StringIO()
    with redirect_stdout(out):
        rc = cli.main(["validate", str(bad)])
    assert rc == 1
    assert "missing required key 'org'" in out.getvalue()


def test_cli_generate_creates_files(tmp_path):
    rc = cli.main(["generate", DEFINITION, "--out", str(tmp_path)])
    assert rc == 0
    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "faq.html").exists()
    assert (tmp_path / "people.html").exists()


def test_cli_generate_refuses_on_invalid_unless_skipped(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"hub": {"title": "x"}}), encoding="utf-8")
    out_dir = tmp_path / "out"
    rc = cli.main(["generate", str(bad), "--out", str(out_dir)])
    assert rc == 1
    assert not out_dir.exists()
    # Bypass with --skip-validation: generation proceeds even though parsing may fail.
    out2 = tmp_path / "out2"
    out2.mkdir()
    try:
        cli.main(["generate", str(bad), "--out", str(out2), "--skip-validation"])
    except (KeyError, AttributeError):
        # The blueprint is too broken to parse — that's the user's choice when
        # bypassing validation; the CLI did its job by warning them off.
        pass
