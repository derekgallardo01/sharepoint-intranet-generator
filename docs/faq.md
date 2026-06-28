# FAQ

## Why generate static HTML instead of provisioning the SharePoint site directly?

Stakeholder agreement happens faster on a clickable preview than on a
written spec. Provisioning the real SharePoint site is a one-way
operation; getting it wrong costs hours of cleanup. Preview-then-
provision means design-by-committee resolves in browser-clicks, not
slack threads, and the production site is provisioned ONCE from an
agreed source-of-truth definition.

## What does the validator actually check?

Structural + reference rules, all listed in `intranet_gen/validate.py`:
- top-level required keys (`org`, `hub`)
- every navigation entry's `page` resolves to a real section / news /
  faq / people / document center / home
- section `key` and `title` present, section keys unique
- news items have a `title`
- document-center library `ownedBy` references an existing section
- FAQ pages have at least one well-formed `{q, a}` entry
- person-directory entries have a `name`

The eval set covers a positive case + each negative class.

## How do I add a new page type?

Three places:
1. Add a dataclass to `intranet_gen/model.py` (mirror `FaqEntry` /
   `Person`) and extend `Site` with the new field(s).
2. Add a `render_<type>(net, site)` function to
   `intranet_gen/render.py`. Add a branch to `render_site` that
   dispatches on `site.type`.
3. Add a `_check_<type>_sections` function to
   `intranet_gen/validate.py` and call it from `validate(...)`.

The FAQ and Person Directory page types are good worked examples — each
is ~30 lines split across the three files.

## What's in `examples/` vs `site-definition.json`?

The top-level `site-definition.json` is the **default** definition
(Meridian Advisory). `examples/` holds the **alternate** worked
definition(s) — currently the Acme Manufacturing one. Add your own
under `examples/` and run them via `python cli.py generate examples/
your-def.json --out out/your-name`.

## Can I change the look (colors, fonts)?

`theme.primary` and `theme.accent` in the definition drive CSS
variables in `_css(theme)`. For a deeper restyle, edit `_css()`
directly. The stylesheet is intentionally inline (no external CSS) so
the `out/` folder works offline.

## Does this work for a non-Microsoft intranet (Confluence, Notion, etc.)?

The HTML output is plain — it'll render anywhere. The deploy-guide is
specific to SharePoint, so a non-Microsoft destination would need its
own provisioning script, but the *definition file format* is portable.

## How do I trigger the screenshot workflow?

```
gh workflow run screenshots.yml --repo derekgallardo01/sharepoint-intranet-generator
```

Or manually from the Actions UI. It uses Playwright to capture 7 PNGs
across both worked definitions and commits them to `docs/screenshots/`.

## Will the validator catch a typo in a doc title?

No — content is opaque to the validator (it only checks structural
correctness). For content review, that's what the HTML preview is for —
click through it.
