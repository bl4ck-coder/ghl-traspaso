# GHL shape (route B: native skeleton + class hooks + small code islands)

Chosen by Nacho on 24/11 («vamos B»). Principle: do not translate arbitrary HTML. Build the page **in GHL's shape from the start**, so that moving it into Sites is close to 1:1 and the client edits every text, image and button natively. Evidence: `base-2026-11-18/39-traductor-ghl/INFORME.md` (measured on 11 GHL-built Sites pages, the ADICIO page GHL publishes, and the public builder bundle) and `references/builder-facts.md`.

Check a page with `scripts/revisar_forma_ghl.py PAGE.html [css ...]` (exit 1 = errors). Rule ids below match its output.

## Map: our piece → GHL native → where its look goes
| ours | GHL | styling |
|---|---|---|
| `<section>` | Section, full width | fields; decorative CSS by Custom Class |
| a row of columns | Row + Columns in %, inner `max-width:1170px` | fields; gaps/align by class |
| `h1`–`h6` | Headline (H tag from the toolbar) | font/size/colour fields (size = 2 numbers: desktop, mobile) |
| `p` | Paragraph / Sub-Headline | fields; inline only bold/italic/underline/colour/font/size/link |
| button-like `a` | Button (URL, phone, `scroll-to-element`) | fields + class |
| `img` (incl. SVG) | Image, file uploaded to Media | fields + class |
| `ul`/`ol` | Bullet List | fields |
| FAQ (`details`) | FAQ element | fields; our accordion motion hooks its DOM |
| `form` | native Form (reconnect at handoff) | form styling |
| video | Video | fields |
| grid with spanning cells, overlaps, a line crossing sections, canvas/WebGL | **island**: one small Custom Code block | reads its text/colours from neighbouring natives or Custom Values |
| `table`, `address`, `blockquote` | paragraph with a class | semantics lost (GHL publishes only `div`) |

Colours: put the palette in Global Custom Colors (two-way synced); GHL ships it as `--brand-*` vars, so class CSS uses `var(--brand-…)`. Fonts: Google Fonts via the page font fields; own fonts as `.woff2` in Media plus `@font-face` in site CSS.

## Rules
- **R1 · No markup inside text** [probado, builder bundle]. The text editor (TipTap) keeps only link href/target/rel, heading level, span colour/font/size, alignment and basic marks. Any `class`, `id` or `data-*` inside a headline or paragraph has no schema slot; 0 of 817 GHL texts carry one. It survives publishing, then vanishes the first time someone edits that block. Fix: put the class on the element; split words/letters with JS at runtime on the published text; a styled suffix («20**+**») is a separate element or a CSS `::after` by class.
- **R2 · `anim-*` hooks on elements only.** Custom Class lives in `extra.customClass.value`, outside the text, and survives edits (421 elements on GHL's own pages use it). It lands on the `.text-output` div for texts (inside: `<div><h1>`), on the outer wrapper for rows/columns. The layer selects `.anim-x h1, .anim-x p`, never `.anim-x` alone for text.
- **R3 · Anchors are actions** [probado]. GHL buttons have no `href="#…"`; they use `scroll-to-element` with the section id. List every in-page anchor in the manifest with the section id to set.
- **R4 · Rows and columns, not grid** [probado]. Only % columns inside rows. Spanning cells, overlaps (a card over the hero photo) and `position:absolute` elements have no field: redesign as row/columns, or keep as CSS by class, or make a small island.
- **R5 · Three width bands** (≤767, 768–1024, ≥1025) [probado]. Anything editable follows those; extra breakpoints and `clamp()` live only in site CSS by class and are lost if the client changes the field.
- **R6 · No semantic tags.** GHL publishes only `div` (0 header/nav/main/section/footer/article). What weighs for SEO survives: H1–H6, alt, real text, links. FAQ → FAQ element.
- **R7 · Images paint without scrolling.** No `loading="lazy"` or `decoding="async"` (a capture or a vision import leaves them blank). Every image has `alt`; decorative ones `alt=""`.
- **R8 · Exactly one H1, no skipped levels.**
- **R9 · Never style by id.** Our ids do not reach GHL; GHL's `heading-XXXX` ids change when an element is duplicated. Class first; GHL id only as the generated fallback below.
- **R10 · Fail safe.** Nothing is hidden unless the JS gate class (`html.capa-activa`) is on. With «Optimize page load» (`isOptimisePageLoad: true` on ADICIO) hydration waits for the visitor's first touch or scroll; JS may never run.
- **R11 · No text baked into images or backgrounds.**
- **R12 · Code placement.** Layer JS/CSS: one pinned jsDelivr file loaded from the **site** Body tracking code (page code is not copied when a page is cloned). JSON-LD: the page's own `schemaMarkup` field [probado: field exists, ADICIO's is `null`], built only from visible data.

## Animation layer in GHL
- Start on `hydrationDone`, with a ~2.5 s fallback. Hydration does not wipe the layer's additions: classes, `data-` attributes and a heading split into word `<span>`s survived hydration and a full scroll (195/195, 253/253) [probado]. GHL only re-renders empty filler spans and form inputs.
- Make every block idempotent (mark done on the element; running twice adds nothing).
- GHL itself runs GSAP + ScrollTrigger + `hydrationDone` on its Sites page conversation-ai [probado]; `position: sticky` by class inside a GHL row works (pinned 500 px there).
- Native GHL animation (animate.css via `data-animation-class`) stays empty on any element the layer animates.
- `files.leadconnectorhq.com` answers `access-control-allow-origin: *`, so the layer can `fetch` an SVG uploaded to Media and animate its paths.
- Honour `prefers-reduced-motion`; pause smooth scroll on `popup-opened`; animate the form box, not its iframe fields.
- Scroll smoothness measured on GHL-published pages: p50 13.3 ms, p95 13.4 ms; long frames only on first load (160–200 ms).

## If a class goes missing (plan, untested)
1. Double anchor: after the page exists in GHL, read its published HTML and write a map `class → GHL element id` into the site CSS/JS as a second selector (`.anim-x h1, #heading-XXXX h1`). Editing text keeps the id (the editor tracks `elementId`); duplicating an element probably changes it.
2. Third: `manifiesto.json` (section, type, order, expected text). If neither class nor id is found, the layer finds the element by position and logs it.
3. Fail safe: a block whose hook is missing stays static and visible (R10), never broken.
4. Re-run the checks on the published URL after every client edit round: `31-adicio-home-ghl/C/comparar.py` and `verificar_seo.py`.

## Worked example: ADICIO home (`31-adicio-home-ghl/sitio/importar.html` + `estilos.css`, 24/11)
`revisar_forma_ghl.py` gave 1 error and 7 warnings:
- R1: 5 marks inside text — a classed link around «Daniel Liboreiro» and the four classed «+»/«%» suffixes in the figures (they would be lost on the first edit);
- R4: 31 grid rules (3 with spanning cells) and 5 absolute elements;
- R5: 12 breakpoints outside GHL's 3 bands and 37 `clamp()`;
- R6: `details`×3, `table`, `address`, `blockquote`;
- R3: 7 in-page anchors.
The page was built before route B. Reshape it with this list before moving it.

## ADICIO pilot: verification limits
- Two sections / 34 elements: generated `sectionStyles` was empty; the editor save generated styles for both sections. That proved the native tree could be saved and styled, not visual or motion parity (`40-adicio-ghl-api/ESTADO.md`, E40-02).
- Reuse `C/comparar.py` as a baseline, not as the final gate: it uses one desktop width and fuzzy copy matching. For programmatic transfers compare by source-to-GHL ID map where available, verify actual loaded fonts and anchors, and test each width and animation separately. Normalize equivalent family-name casing in reports; the computed family name alone does not show the font actually loaded.
- Still unverified: a text edit → save → reopen retains classes and behavior on ADICIO; duplicate ID behavior; Custom Code size limit. The map is an image with a static fallback, but its interactive code also looks for `[data-zona]` and `.zona-nombre`; adapt those hooks to the actual GHL markup and test mouse, touch and keyboard. CORS on other media is not proof the final map URL works.
