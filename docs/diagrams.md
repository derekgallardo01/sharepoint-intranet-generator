# Diagrams

Beyond the inline ones in [architecture.md](architecture.md).

## 1. Class-ish model — definition.json → typed Intranet

```mermaid
classDiagram
    class Intranet {
      +str org
      +str tenant
      +dict theme
      +dict hub
      +list~NavLink~ nav
      +list~Site~ sites
      +DocumentCenter document_center
      +list~NewsItem~ news
    }
    class Site {
      +str key
      +str title
      +str type
      +list~Library~ libraries
      +list~FaqEntry~ questions
      +list~Person~ people
    }
    class FaqEntry { +str q; +str a }
    class Person { +str name; +str title; +str email; +str photo_url }
    class Library { +str name; +list~Column~ columns }
    class Column { +str name; +str type; +bool required }
    class DocumentCenter {
      +str key
      +str title
      +list~DocLibrary~ libraries
    }
    class NavLink { +str label; +str page }
    class NewsItem { +str title; +str date; +str summary }

    Intranet --> Site
    Intranet --> NavLink
    Intranet --> NewsItem
    Intranet --> DocumentCenter
    Site --> Library
    Site --> FaqEntry
    Site --> Person
    Library --> Column
```

## 2. Render dispatcher — which renderer fires per site type

```mermaid
flowchart TB
    RA["render_all(net)"] --> RH["render_home → index.html"]
    RA --> LOOP["for each Site in net.sites"]
    LOOP --> RS["render_site(net, site)"]
    RS --> D{"site.type?"}
    D -- "'section' (default)" --> SEC["render_section<br/>(libraries + columns + links + permissions)"]
    D -- "'faq'" --> FAQ["render_faq<br/>(details/summary accordion)"]
    D -- "'people'" --> PPL["render_people<br/>(card grid with photo + email)"]
    SEC --> KEY["pages[site.key + '.html']"]
    FAQ --> KEY
    PPL --> KEY
    RA --> NEWS["news.html (reuses home news block)"]
    RA --> DC["render_document_center → document-center.html"]
```

## 3. Sequence — validate → generate happy path

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant CLI as cli.py
    participant V as validate
    participant LI as load_intranet
    participant R as render_all
    participant FS as filesystem

    U->>CLI: cli.py generate site-definition.json --out out/
    CLI->>V: validate(definition_path)
    V-->>CLI: [] (no errors)
    CLI->>LI: load_intranet(definition_path)
    LI-->>CLI: Intranet model
    CLI->>R: render_all(intranet)
    R-->>CLI: {filename: html, ...} (8 pages)
    loop for each (filename, html)
      CLI->>FS: write out/<filename>
    end
    CLI-->>U: "Generated 8 page(s) into out/"
```

## 4. Sequence — validation blocks generation

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant CLI as cli.py
    participant V as validate

    U->>CLI: cli.py generate broken.json --out out/
    CLI->>V: validate(definition_path)
    V-->>CLI: [ValidationError(...) x3]
    CLI->>CLI: filter to blocking severity="error"
    CLI-->>U: "Refusing to generate: definition has blocking errors:"
    CLI-->>U: "  [error] sites[1].key: duplicate section key 'hr'"
    CLI-->>U: "  ..."
    CLI-->>U: "Re-run with --skip-validation to bypass."
    Note over U: User fixes the definition, re-runs.
```

## 5. State — definition lifecycle from sketch to provisioned tenant

```mermaid
stateDiagram-v2
    [*] --> Sketch: brand-new client engagement
    Sketch --> Draft: definition.json drafted
    Draft --> Invalid: edits introduce errors
    Invalid --> Draft: validator output guides fix
    Draft --> Valid: validator returns []
    Valid --> Reviewed: HTML preview clicked through by stakeholders
    Reviewed --> Valid: changes requested
    Reviewed --> Provisioned: deploy-guide.md run against real tenant
    Provisioned --> Maintained: changes flow through the same definition
    Maintained --> Draft: definition edited
```
