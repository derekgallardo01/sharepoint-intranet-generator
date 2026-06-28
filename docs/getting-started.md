# Getting started

A 5-minute walkthrough — no SharePoint Online tenant required.

## 1. Clone and run

```bash
git clone https://github.com/derekgallardo01/sharepoint-intranet-generator.git
cd sharepoint-intranet-generator
python run.py
```

You should see 8 pages generated under `out/`:

```
index.html · hr.html · it.html · policies.html · faq.html · people.html · news.html · document-center.html
```

Open `out/index.html` in a browser to click through the proposed
intranet.

## 2. Validate any definition

```bash
python cli.py validate site-definition.json
```

`OK: site-definition.json is structurally valid.`

The linter checks: missing required keys (`org`, `hub`), duplicate
section keys, nav links pointing at undefined sections, FAQ entries
missing `q` or `a`, person entries missing `name`, document-center
libraries owned by unknown sections, news items missing titles.

## 3. Try the alternate worked example

There's a second worked definition for a manufacturing company:

```bash
python cli.py generate examples/site-definition-acme-manufacturing.json --out out/acme
```

9 pages including Production, Quality, Supply Chain, Engineering, plant
FAQ, and plant directory.

## 4. Run the eval set

```bash
python evals/run.py
```

`Eval: 14/14 passed (100%)`. Cases cover valid + each negative class
(missing org, duplicate section keys, nav pointing at undefined section,
FAQ without questions, etc).

## 5. See the live demos

The CI deploys both worked definitions on every push:

- https://derekgallardo01.github.io/sharepoint-intranet-generator/

Two rendered intranets you can click through, no Python required.

## 6. Run in Docker (optional)

```bash
docker build -t sharepoint-intranet-generator .
docker run --rm -v $(pwd)/out:/app/out sharepoint-intranet-generator
```

## What to read next

- [Architecture](architecture.md) · [Customization](customization.md) ·
  [Evaluation](evaluation.md) · [Diagrams](diagrams.md) · [FAQ](faq.md)

## Bringing it to a real tenant

Agree the structure from the HTML preview, then provision the SharePoint
site per [`deploy-guide.md`](../deploy-guide.md) — same definition file
is the spec.
