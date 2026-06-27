# Intranet governance

The rules that keep the intranet clean as it grows. Tailor the specifics per
client, but keep the model.

## Naming conventions

| Object | Convention | Example |
|--------|------------|---------|
| Hub site | `<Org> Intranet` | `Meridian Intranet` |
| Section site URL | `/<section>` lowercase, no spaces | `/hr`, `/it`, `/policies` |
| Library | Title Case, no "library" suffix | `Controlled Policies` |
| List | Title Case, plural | `Service Requests` |
| Content type | `<Org> <Type>` | `Meridian Policy` |
| Metadata column | Title Case, no prefixes | `Review Date`, `Owner` |
| Microsoft 365 group | `<Org>-<Section>-<Role>` | `Meridian-HR-Owners` |

Rules: no personal names in site/library names; no dates in titles (dates are
metadata); avoid abbreviations that won't survive staff turnover.

## Permissions model

Permission is granted to **groups**, never to individuals, and at the **site**
level, not per item. Three standard roles per section:

| Role | SharePoint level | Who |
|------|------------------|-----|
| Owners | Full control | 1–2 people who own the section |
| Members | Edit | the team that maintains content |
| Visitors | Read | everyone else (usually a company-wide group) |

- The hub gives **read** to the whole company by default; sensitive sections (HR,
  Contracts) break inheritance and restrict Members/Visitors.
- No "Everyone except external users" on anything containing personal or
  contractual data.
- External sharing is **off** at the site level unless a specific library needs it.

## Lifecycle

```
Propose → Provision → Populate → Review (quarterly) → Archive/Retire
```

- **Provision** from the blueprint (`site-definition.json`) so every section is
  created the same way.
- **Review** quarterly: an owner is named on every library; libraries with a
  `Review Date` column surface what's overdue.
- **Archive** a section by setting it read-only and moving it under an "Archive"
  hub node; delete only after the retention period.

## Document management

- **Content types** carry the columns and (optionally) a retention label, so every
  document of a type behaves consistently. Prefer content types over ad-hoc columns.
- **Metadata over folders.** Libraries are flat; documents are found by filtering on
  columns (`Department`, `Owner`, `Status`, `Review Date`), not by folder path.
- **Standard metadata columns** every controlled library should have:
  `Title`, `Department`, `Owner` (person), `Status` (Draft / Approved / Retired),
  `Effective Date`, `Review Date`.
- **Retention.** Apply retention labels to Policies and Contracts (e.g. keep 7
  years after effective date); everything else inherits a short default. Retention
  is set on the content type or library, never per file by hand.
- **Versioning** on for all libraries; major+minor on controlled-policy libraries
  so drafts and published versions are distinct.

## Do / don't

- ✅ Grant access to groups; ✅ find documents by metadata; ✅ name one owner per
  library; ✅ provision from the blueprint.
- ❌ Per-user permissions; ❌ deep folder trees; ❌ dates in titles; ❌ external
  sharing left on by default; ❌ unique permissions on individual items.
