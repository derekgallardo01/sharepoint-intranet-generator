# Deploy guide — standing the intranet up in a tenant

This turns `site-definition.json` into a live modern intranet. Steps are written
for the SharePoint admin center + site UI; they map 1:1 to PnP PowerShell /
PnP provisioning templates if you prefer to script it.

**Prerequisites:** SharePoint Administrator role; the tailored `site-definition.json`;
the Microsoft 365 groups for each section's Owners/Members; the org logo + theme
colors. Review [`governance.md`](governance.md) first — it defines naming and
permissions referenced below.

## Steps

1. **Create the hub communication site.**
   New site → *Communication site* → name it `<Org> Intranet` (matches the `hub`
   block in the blueprint). Apply the org theme/logo.

2. **Register it as a hub.**
   SharePoint admin center → Active sites → select the site → *Register as hub
   site*. Set who can associate sites.

3. **Create each section site.**
   For every entry in `sites[]`, create a *Communication site* with the URL from
   the blueprint (`/hr`, `/it`, `/policies`, `/document-center`, …) and **associate
   it to the hub** (Settings → Hub site association).

4. **Create lists and libraries.**
   On each site, create the lists/libraries from that site's `lists` block. For
   each library, add the **columns** exactly as specified (name + type + required),
   then turn on **versioning**.

5. **Create content types & metadata.**
   In the content-type gallery, create the content types named in the blueprint
   (e.g. `<Org> Policy`) with their columns, and attach each to its library. This is
   what makes the Document Center metadata-driven instead of folder-driven.

6. **Build navigation.**
   On the hub, set the **global (hub) navigation** to the `navigation.global`
   entries so every site shares one top menu. Set each site's local navigation from
   its `navigation` block.

7. **Add pages and web parts.**
   For each entry in `pages[]`, create/edit the page with the given layout and add
   the web parts per section (Hero, News, Quick links, Document library view). The
   home page is the hub's site home.

8. **Apply permissions.**
   For each site, set Owners / Members / Visitors to the groups in the
   `permissions` block. Break inheritance on sensitive sites (HR, Contracts) and
   confirm external sharing is off unless required.

9. **Apply retention.**
   In the compliance/purview center, create the retention labels referenced in the
   blueprint's governance notes and publish them to the Policies and Contracts
   libraries (or set them on the content type).

10. **Populate + validate.**
    Upload representative documents, set their metadata, and confirm a non-admin
    test user sees exactly what they should. Record the handover walkthrough
    (see [`DEMO.md`](DEMO.md) for the structure).

## Checklist

- [ ] Hub communication site created, themed, branded
- [ ] Site registered as a hub
- [ ] Every section site created with the blueprint URL
- [ ] Every section site associated to the hub
- [ ] All libraries/lists created with their columns
- [ ] Versioning enabled on every library
- [ ] Content types created and attached to libraries
- [ ] Global (hub) navigation matches `navigation.global`
- [ ] Per-site navigation set
- [ ] Home page + section pages built with web parts
- [ ] Owners / Members / Visitors groups assigned per site
- [ ] Inheritance broken + external sharing off on sensitive sites
- [ ] Retention labels published to Policies and Contracts
- [ ] Sample documents uploaded with metadata
- [ ] Non-admin test user permission-check passed
- [ ] Handover walkthrough recorded and shared
