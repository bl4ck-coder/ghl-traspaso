---
name: gohighlevel-pages
description: "Use when a page built here must be editable in GoHighLevel."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [gohighlevel, ghl, funnels, websites, landing-page, animation, gsap]
    related_skills: [memoria-de-diseno, gusto-marca, revisar-antes-de-entregar, grounded-citations, model-routing]
---

# Pages built in Hermes, editable in GoHighLevel (Sites and Funnels)

## When to Use
- He wants a page (often an improved version of a reference URL) built here and then moved into GHL Sites or Funnels.
- Any question about what GHL keeps editable, how animations live inside GHL, or whether Hermes can create GHL pages by API.

Nacho wants the best of both: a page designed and animated here (his taste, the atlas, the design skills, two blind reviewers) that lands in GHL as native elements, so he or a client can later change every headline, subtitle, colour and H1/H2 without code. Sites and Funnels share one builder, so every rule here applies to both unless marked.

**Default shape:** build for native rows, columns and editable elements from the start. Use element-level Custom Classes and small code islands only for features with no native counterpart. Run `scripts/revisar_forma_ghl.py PAGE.html CSS…` before transfer; it checks the source shape, not the result in GHL. See `references/forma-ghl.md` for the rules and fallback plan.

**Keep the transfer routes separate:** a native draft write is proven feasible with page-scoped CSS/JS bridges (`references/internal-api.md`); it does not prove an exact clone or validate Start from URL. Ask AI from an image is approximate. Pick the route for the required editability and fidelity, then verify it on the actual destination.

Full research with verbatim, re-checked quotes: vault `01-Projects/Hermes/base-2026-11-18/29-ghl-paginas/` (`SINTESIS.md`, fronts `A-desde-url` … `F-sonda`, each with `informe.md` and `fuentes.json`). Read `SINTESIS.md` before redoing any of it.

Third-party GHL tools (repos, MCP servers, extensions, skills) were surveyed against our open problems (ids P01–P25 in `38-repos-ghl/COMUN-38.md`; per-group `informes/`, then `SINTESIS.md`). Read that before answering «does some tool already do X», and extend it with the `prior-art-repo-survey` skill. A tool that writes pages through the internal editor API or drives the UI is reported as «solved, but breaks the terms»; one that wraps our HTML in a code block solves import but not native editing.

## Always-on rules
- **Never log into his GHL on your own.** In a research phase he said to investigate first. Offer two ways to test: he imports and sends the preview links (no login needed), or Hermes uses a test sub-account from his browser and creates only the test pages. Once he names the account (ADICIO: the Bizurai white-label login, site «ADICIO pruba»), work only in the draft page he points to and never publish. He types password and email code himself (vault or his own hands in a visible window).
- **He wants to watch.** `browser_exec` runs headless: when he asks to see the work, launch a visible Chromium with `--remote-debugging-port=9333` and its own profile, let him log in there, and drive that tab by CDP (`40-adicio-ghl-api/herr/cdp9333.py`, `editor9333.py`). Never tell him a window is open on his PC without checking it has a window title.
- **The brand is the client's.** Reuse the process and tools from earlier design rounds (round folders, briefs, two blind reviewers, wake-up watcher, capture and check scripts), never another project's brand, colours, copy or assets. Say this in the common brief, and have any inventory child split «reusable for any brand» from «specific to that project».
- **Editable means native.** Text inside a Custom JS/HTML block cannot be edited by the client without code. Anything he wants editable must be a native element (Headline, Sub-Headline, Paragraph, Button, Image, Video, List).
- **The editor's internal API needs his explicit OK** (reverse-engineered page JSON). It writes native pages, but GHL's terms forbid it and it uses the user's full session. A custom MCP that wraps it carries the same risk: what matters is what it does inside. Before he decides, say a test sub-account does not isolate the risk (the penalty suspends the whole Platform Account). He accepted that risk for ADICIO and chose this route; the working pipeline is `references/internal-api.md`. The robots clause («any robot, spider or other automatic device … to access the Platform») does not care whose content it is, and it also covers Hermes driving the editor with computer-use. When he asks about it, quote the two clauses verbatim (`references/builder-facts.md`) and say the reverse-engineering one is arguable and the robots one is not.
- Every claim about GHL carries a level: oficial (help center, changelog, API docs), reportado (community, video, GHL's own support AI), probado (we measured it), no encontrado.
- **Keep shape validation, native save, visual parity, motion parity, SEO and edit/save/reopen separate.** Nacho reviews both the live draft preview and the GHL editing canvas; test both at desktop, tablet and mobile sizes before calling a migration faithful. Compare against the approved original using its responsive CSS, not styles reconstructed from screenshots. Matching boxes do not prove matching line breaks or painted imagery; mounted effects do not prove matching motion. Drive the same scroll and interactions on both versions, compare intermediate and final states, and report exactly which effects and surfaces remain unverified. A section passing is the gate to scale, not proof for the whole page.
- **Only his GHL result says it works.** When a step runs in his GHL (import, preview), report what you changed and verified on your side and ask him to retry. Never say «ya lo arreglé» until his retry or the request log shows GHL passed: a URL that answers 200 to curl was still refused.
- **One page first.** Run the home alone through the whole route (build → publish → import → measure) and show him the result before building the other pages: he wants to see the route work on one page before the rest.

## Procedure
1. **Ask up front, in one clarify:** the reference URL; destination (Site, Funnel or both); whether Hermes may enter a test sub-account; how much the content may change. Then work without stopping.
   - When he says the reference is open in his browser, read the URL yourself instead of asking: `computer_use` `list_windows`, then `capture` with that window's `pid` and `window_id` (a capture by app name alone can miss the window), and read the address bar.
   - Content: he answered (ADICIO, 20/11) «mantener el mismo copy o lo más que puedas, respetando cómo utilizan los h1 h2 y todas las técnicas de SEO y AI SEO». Make that the default:
     - the client's copy word for word; only duplicates, broken or empty bits and evident typos change, each one logged (before → after → reason);
     - redundant copy may go when he asks for less repetition: an eyebrow that restates the H1, a sentence that repeats a button's label, a card that repeats a figure shown in another section. He approved removing exactly those from the ADICIO hero. Log each removal in `cambios-texto.md`, keep the H1/H2 and SEO checks passing, and the reviewer lists it as a minor finding for him to confirm, never a blocker;
     - the client's heading levels kept: the same H1 and the same H2s, H3/H4 as in the reference, raised only to avoid skipped levels;
     - no invented data;
     - a reviewer's request that needs content the page lacks (where the client works, shown in the hero) is met only by moving the client's own words up, logged as an addition, and put to him to approve; if his words do not cover it, the builder answers «en desacuerdo» with evidence instead of writing new copy;
     - when the desktop and mobile copies of one block differ, merge what only one carries; if they contradict, keep one, log both in `cambios-texto.md` and put the choice to him.
     Before briefing, audit the reference's headings and SEO from its server HTML: H list in order, `lang`, title and description, JSON-LD, alts, landmarks. Write the audit to `referencia/seo-ref.md`; the ADICIO reference had `lang=en`, a filler title and description, 30 `alt="Logo"` and no schema.
   - If his answer arrives after the builder started, add it to `correcciones-nacho.md` and the briefs, then kill only that `claude.exe` (`taskkill /T` on its PID; match its command line and exclude your own PowerShell). The pipeline's `<name>2` step resumes the same session with «Releé correcciones». Raise that step's turn cap in `topes.txt` before killing it: the cap is read at call time.
2. **Design the improved page with the usual pipeline** (capture the reference, `memoria-de-diseno`, the atlas, the creative skills, build, two blind reviewers). The builder's brief adds the GHL shape of step 3.
   - Before designing, look for an earlier case of the same client (`Design-Agent/casos/<cliente>/`) and search what he said of its variants: do not bring back what he rejected.
   - Capture the reference with the scripts in `31-adicio-home-ghl/referencia/`: `capturar_ref.py` (full-page shots and structure) and `contenido_ref.py` (visible text, images and links per section at 1920 and 390); download its assets next to them. A reference that is itself a GHL page (`sites.leadconnectorhq.com/preview/<id>`) is server-rendered, so a plain `curl` gets its full HTML.
3. **Shape the HTML for the rebuild** following `references/forma-ghl.md` and run `scripts/revisar_forma_ghl.py` until it exits 0; fix every warning or log why it stays (island, CSS by class). Older wording, still valid: stacked full-width sections; simple pieces that map to native elements; real `<h1>`/`<h2>` tags (H1-H6 is chosen per headline in GHL, but only if it arrives as a headline); real text, never text baked into images; all content visible in the server HTML without JS; animation kept in a separate layer (step 6), never needed to show content. Each animatable element gets a stable `anim-*` class.
   - Ship an importable twin (`importar.html`): the same HTML without the animation layer and without `loading="lazy"` or `decoding="async"` on images. A Chromium full-page screenshot taken without scrolling leaves async-decoded images blank [probado], and a rebuild by vision may read the page exactly that way. Strip the same hints from `index.html` too: they blank it with JS off.
3b. **SEO and AI SEO, on both sides.**
   - In the page `<head>`: `lang`; a real title and description made from the client's own sentences; Open Graph; one JSON-LD `@graph` built only from data shown on the page, with FAQPage identical to the visible Q&A. People's roles and titles use the page's exact word (a person the page calls «responsable» is not `founder` in the schema).
   - In the body: descriptive alts, semantic landmarks, answers that stand alone in the server HTML, and LCP/CLS measured.
   - Also a `SEO-GHL.md` to paste, because we do not know whether Start from URL carries the `<head>`. Official GHL places (seen via search, confirm before citing):
     - «SEO Meta Data» icon in the builder: help article 48001073924;
     - native «Schema Markup Generator»: article 155000007406;
     - HTML `lang` attribute selector: changelog «SEO Suggester and HTML Language Attribute Selector».
   - The builder ships a `verificar_seo.py` tested on known truth. It must flag the reference, pass the new page and catch, each on a mutated copy: one client sentence changed, two FAQ answers swapped between their questions (in the visible Q&A and in FAQPage), and the icon-only links (social icons with no text) removed. A checker that only counts texts and totals passes the last two. Its source copy is the union of each section's texts at 1920 and at 390: GHL pages often carry a desktop and a mobile copy of the same block with different words, and a check against one breakpoint passes while content that exists only in the other is dropped.
   - After import, diff GHL's text against the client's copy too, not only against our page.
4. **Publish on a public URL, instrumented.**
   - Vercel production deploy: copy `sitio/` into a folder named after the project (`31-adicio-home-ghl/publicar-vercel/adicio-ghl-prueba/`), make `index.html` the importable twin (the animated one as `animado.html`) so the bare domain works, and run `vercel deploy --prod --yes` there. Hand over only the short alias (`https://<project>.vercel.app`): the team-scoped aliases answer 302 with `X-Robots-Tag: noindex`.
   - Before handing over, check `/`, `/importar.html` and every asset in parallel (`xargs -P 40 curl`) return 200 with no `X-Robots-Tag`. A `python -m http.server` behind a quick tunnel refuses part of a 38-file burst (`dial tcp ... connectex` in the tunnel log), and the trycloudflare edge adds `X-Robots-Tag: none`. Keep the tunnel (`publicar.ps1`) only as a fallback.
   - Log every request from the first deploy: copy `templates/vercel-middleware-log.js` as `middleware.js` into the deploy folder, then run `scripts/vigilar_pedidos.py` in the background (`terminal background=true notify=true`). Without the log, a failed import cannot say whether GHL even fetched the page.
   - Count only requests to the short alias, minus your own IP and tool user agents. A HeadlessChrome burst from an AWS US IP to the hash alias (`<project>-<hash>-<team>.vercel.app`) right after each deploy is Vercel's own screenshot bot, not GHL.
   - If GHL answers «No hemos podido comprobar este enlace», ask him to retry with «Previsualizar» on our URL and on a control (the client's live site). Read the log: no request means the check fails before reaching us (feature or account); our page failing while the control passes means it is ours. On ADICIO (24/11) the control failed too and no GHL request reached Vercel in 25 minutes: the Beta failed on GHL's side, so changing our page does not help. Switch to import from image (route table).
5. **Import and measure.** «Empezar desde una URL / Start from a URL» in a Site and in a Funnel. Compare the published preview against a manifest of expected values (per element: id, native type expected, text, colour, font, size, H tag), element by element: native or not, text identical or rewritten, colour, font, H tag, class kept, and whether JS ran (a footer witness that JS rewrites, plus a section only JS inserts). The rebuild is AI-by-vision, so diff every text against the source before handoff. The probe page and its 97-element manifest exist: `29-ghl-paginas/F-sonda/` (`publicar.ps1`, `manifiesto.json`, `capturar.py`). The comparator is not written yet.
6. **Adapt and test the animation layer** (`references/builder-facts.md`, Animation-layer contract). Generate from the approved source, keep timing and keyframes, and adapt only the hooks, lifecycle and widgets that GHL changes. Use stable Custom Classes, split text at runtime and keep content visible without animation. Load once, but remount per effect on live nodes when GHL replaces a section. Test in memory before saving, then repeat from a fresh preview with no injected code. Compare the same scroll path and user inputs against the original, including reverse scroll, keyboard and reduced motion. Keep complex effects in small code islands that do not replace editable content.
7. **Hand off** with the funnel share link or a snapshot (sites and funnels). Forms must be reconnected in the destination account.

## Route choice (show him the comparison, not just the pick)
| route | client edits text/colour without code | animations |
|---|---|---|
| route B: GHL-shaped page (`forma-ghl.md`) rebuilt natively + animation layer by class (default) | yes | yes, via the layer; islands for the rest |
| GHL-shaped HTML + Start from URL + animation layer | yes | yes, via the layer; the Beta failed on GHL's side on 24/11 |
| section screenshots + builder «Ask AI» → Build → attach image (when Start from URL fails) | yes; close, not identical | yes, via the layer |
| whole page in one Custom HTML block | no | full |
| build by hand in the GHL editor | yes | yes, via the layer; slow |
| internal editor API (`references/internal-api.md`) | yes, native; whole ADICIO home written to a draft; appearance needs CSS bridges and a pass in preview AND editor | via page CSS/JS and Body code; parity tested per section; terms risk he accepted |
| GHL AI Studio | yes, in its editor | yes; its projects do not move to Sites or Funnels. He ruled it out for ADICIO: «tiene que ser sitios» (24/11) |

## Team rules (Caro, meeting 25/11; cites = line in `transcripcion-wispr.txt`)
- Pick the CORRECT native element, not just a native one: forms and checkout from GHL (L126, 450, 605-611), calendar for bookings (L608), blog list = Blog post > «Recent posts by category» (L319-320), newsletter = «Subscribe to email list», not a generic form (L451-454).
- Every element has a workflow behind it; workflows live in a folder per site, and form and workflow share the same number and name (L499-500, 557-564).
- One H2 per section even if it wraps to 2-3 lines (Shift+Enter keeps one tag); sub-items inside a section are H3 (L208-229, 245-248).
- SEO: meta title 50-60 chars (44 reads as short), meta description up to 155, page under 2 MB total (L211-217).
- Hand cursor only on real links, never on hover-effect cards (L186-193).
- Descriptive anchor text on internal links, never «click here» (L394-401).
- At least 500 words of useful copy per page, to avoid lean content (L142-144).
- GHL's AI: one element at a time, tell it not to change anything else; small button tweaks by hand (L434-435).
- No WhatsApp links: everything goes to the home's general contact form (L194-197).
- Old blog URLs get a 301 to the new GHL URL (`/blog/b/...`) (L356-367).

## Pitfalls
- GHL's in-app support AI does not know Start from URL (no help article); it answers about the older internal importer, whose «does not import from other websites» belongs to that other feature. Ask it first whether its docs cover the feature by its exact label (`grounded-citations`, vendor support assistants).
- The official API (v3 funnels, 7 endpoints) and the official MCP only list pages, count them and manage redirects: no route creates pages or edits text.
- GHL's own `heading-XXXX` ids change when an element is copied; `.elHeadline`/`.elButton` selectors in tutorials are ClickFunnels, not GHL. Hook by `Custom Class`.
- «Optimize JavaScript» can delay scripts until the visitor interacts: content hidden until JS runs can stay hidden.
- Code added to a single page is not copied when the page is cloned; site/funnel-level tracking code is.
- Text over a photo can pass axe (it reads the CSS background colour) while the pixels under the letters give 2.3:1. Measure contrast on the rendered pixels behind each text box over an image, at both widths.
- Check that images painted by the pixel spread inside each image box on the screenshot (stddev ≈ 0 = flat, unpainted box), never by `img.complete` or `naturalWidth`: both report true for an image the capture left blank. Reusable probe, with and without the attribute, JS on and off, 1920 and 390: `31-adicio-home-ghl/revision/scripts/r_decoding.py` (change its port and output folder).
- «Improve» must not flatten the reference's offer hierarchy: if it shows two main services and two complementary ones, the new page keeps that difference in size and layout. Four identical cards were a blocking finding.
- Links copied from a GHL reference often point to its preview URLs (`sites.leadconnectorhq.com/preview/<id>`). Rewrite each one to the client's live domain and check it answers 200 before handoff.
- The mobile menu: choosing an anchor closes the menu so the target heading is not covered, Escape closes it and returns focus to the toggle, and it works with JS off. Check the target is the element under its own centre (`elementFromPoint`) after the tap, at 390.
- A subscribe or contact box must capture the address (a real `<form>` with inputs), never a `mailto:` link that opens the visitor's mail client and loses the lead. It is reconnected to a native GHL form at handoff (step 7).
- The paste-in Body file goes stale when the layer changes. ADICIO's `C/pegar-en-body.html` from 20/11 lacked three later blocks (magnet, map, contact). Rebuild it with `C/armar_pegar.py` from `sitio/capa/` right before handing it over, and grep it for every `/* N · ` block that `capa.js` has.
- A quick tunnel can fail with «failed to parse quick Tunnel ID: invalid UUID length: 0». It is transient, so rerun the launcher (`31-adicio-home-ghl/publicar.ps1`). Check the downloaded bytes with `curl -o file` + `wc -c`: `%{size_download}` printed 0 through the tunnel even when the content arrived.
- A map or illustration that the animation layer lights up ships as a native Image (an SVG file in `<img>`): it must look complete with the layer off, keep the `viewBox` proportion of its reserved box, and carry any label as paths, since an `<img>` SVG loads no page fonts. Coverage maps use real geography: `taller-forja`, `references/mapas-reales.md`.

Facts with their sources, the animation-layer contract and open questions: `references/builder-facts.md`. Internal-API pipeline and its pitfalls: `references/internal-api.md`. Request logging for the import test: `templates/vercel-middleware-log.js` and `scripts/vigilar_pedidos.py`.
