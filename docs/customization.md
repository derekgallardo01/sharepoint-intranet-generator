# Customization

Six things you'll typically tune per client. Most are JSON edits; the rest are
small additions to [intranet_gen/render.py](../intranet_gen/render.py) or
[intranet_gen/validate.py](../intranet_gen/validate.py).

## 1. Add a new section

Append to `sites` in [site-definition.json](../site-definition.json):

```json
{
  "key": "finance",
  "title": "Finance",
  "url": "/sites/intranet-finance",
  "summary": "Budgets, expense policy, and finance ops.",
  "permissions": { "owners": "Finance-Owners", "members": "Finance-Members", "visitors": "AllStaff" },
  "libraries": [
    { "name": "Finance Documents",
      "columns": [{"name": "Title", "type": "Text", "required": true}] }
  ],
  "links": ["Expense form", "Reimbursement policy"]
}
```

Then add a nav entry under `navigation.global` (validation will block you if
you forget):

```json
{ "label": "Finance", "page": "finance" }
```

## 2. Add a new page type

The pipeline already dispatches on `Site.type`. To add e.g. a calendar page:

1. Add a `CalendarEvent` dataclass to [model.py](../intranet_gen/model.py) and
   extend `Site` with an `events: list[CalendarEvent]` field.
2. Add a `render_calendar(net, site)` function in
   [render.py](../intranet_gen/render.py).
3. Add one line to `render_site`: `if site.type == "calendar": return render_calendar(net, site)`.
4. Add a `_check_calendar_sections` function to
   [validate.py](../intranet_gen/validate.py) (mirror `_check_faq_sections`).

The FAQ and Person Directory implementations are good references — each is
~30 lines split across the three files.

## 3. Theme / branding

`theme.primary` and `theme.accent` in the definition drive the CSS variables
in `_css(theme)`. For a deeper restyle:

- The whole stylesheet is in `_css()` — edit it directly.
- For per-page overrides, add a `theme` field to the section in the JSON and
  read it in the relevant renderer.

Keep it inline (no external stylesheet) so the preview stays self-contained.

## 4. Tighten validation

Add a rule to [validate.py](../intranet_gen/validate.py):

```python
def _check_summary_present(d, errors):
    for i, site in enumerate(d.get("sites", []) or []):
        if isinstance(site, dict) and not site.get("summary"):
            errors.append(ValidationError(
                f"sites[{i}].summary",
                "section should have a summary for the home page card",
                "warning",
            ))
```

Then call it from `validate(...)`. Add an eval case for both the positive and
negative paths to [evals/golden.json](../evals/golden.json) before shipping.

## 5. Provision the real tenant

[deploy-guide.md](../deploy-guide.md) walks the PowerShell / SharePoint Admin
Center steps. The same `site-definition.json` is the source of truth — keep
it under source control alongside the tenant's provisioning scripts, and
re-run validate before each push to production.

## 6. Governance model

[governance.md](../governance.md) has the information-architecture rules
(permissions, naming, retention, lifecycle). When governance rules become
*structural* (e.g. "every section must have an owner"), promote them into
[validate.py](../intranet_gen/validate.py) so they're enforced not advisory.

## Validating any change

```bash
python -m pytest -q
python evals/run.py
python cli.py validate site-definition.json
python run.py
```

If you change a validation rule, the eval set must reflect it. Add the new
positive and negative case to `golden.json` **before** changing the rule.
