# Changelog

Notable changes to the SharePoint intranet generator. Dates are when the
change landed on `main`.

## 2026-06-27 — Live demo
- GitHub Pages live demo at
  https://derekgallardo01.github.io/sharepoint-intranet-generator/ — both
  worked definitions (Meridian Advisory + Acme Manufacturing) rendered on
  every push

## 2026-06-27 — Docker support
- Dockerfile so the generator runs via `docker run` without a Python install
- README "Run in Docker" section

## 2026-06-27 — Second worked definition (manufacturing)
- `examples/site-definition-acme-manufacturing.json` — Production / Quality
  / Supply Chain / Engineering sections + plant FAQ + plant directory + ISO-
  flavoured governance notes
- Test that the alternate definition validates clean and renders all expected
  pages
- CI smoke-tests both the default and the alternate definitions

## 2026-06-27 — GitHub Actions CI
- `.github/workflows/ci.yml` running pytest + eval + smoke-test on Python 3.11
- CI status badge added to README

## 2026-06-27 — Build-out: validation, FAQ + people page types
- `intranet_gen/validate.py` — structural + reference validation with dotted
  JSON paths, error/warning severity
- `FaqEntry` + `Person` dataclasses; `Site` grows `type / questions / people`
  fields
- `render_faq` (details/summary accordion) + `render_people` (card grid);
  `render_site` dispatcher
- `cli.py` with `validate` + `generate` subcommands; generate validates
  first by default
- `evals/golden.json` — 14 inline-JSON validation cases (positive + each
  negative class)
- 9 new tests covering validation, FAQ rendering, people rendering, CLI
- `docs/architecture.md`, `customization.md`, `evaluation.md`
- `docs/sample-run.txt` (validate clean + validate broken + generate +
  new-page snippets)
- README expanded with architecture, sample, eval, customization sections

## 2026-06-27 — Initial public release
- Static HTML intranet generator driven by `site-definition.json`
- Section pages, home, news, document center; inline CSS, no external assets
- Typed dataclass model + deterministic renderer
- `governance.md` + `deploy-guide.md`
- 8 unit tests including XSS escaping
