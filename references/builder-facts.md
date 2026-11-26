# GHL builder facts (Sites and Funnels)

Levels: [oficial] help center / changelog / API docs; [reportado] community, video, support AI; [probado] read from published GHL HTML/JS; [hipótesis] to measure with the probe. Article ids are on help.gohighlevel.com/support/solutions/articles/<id>. Verbatim quotes and download dates live in the vault fronts' `fuentes.json` (`01-Projects/Hermes/base-2026-11-18/29-ghl-paginas/`).

## Start from a URL (Beta)
- [oficial] Clone by vision: changelog «funnel-website-ai-enhanced-page-generation-clone»: «Cloning now threads your customization request through vision analysis and section generation». Help 155000006713: «It does not create an exact clone of the original page or guarantee that every design element, layout, interaction, or piece of content will be reproduced.»
- [reportado] ideas board «import-from-url-should-copy-page-text-exactly»: «the AI rewrites some of the text, changes quotes and alters terms.»
- [oficial] The internal importer (Add step → Create → Import) is a different feature: help 48001209319 «Does not import from other websites/funnel providers».
- [oficial, nearest analogue] The ClickFunnels 2.0 importer carries headlines, paragraphs, lists, image, video, buttons; not icons, menus, countdowns, checkout. [reportado] forms do not come across and mobile often breaks.
- [probado 24/11, ADICIO] The dialog checks the link before rebuilding. On failure it shows «No hemos podido comprobar este enlace en este momento» with «Vuelva a intentarlo» and «Comience en blanco en su lugar». The ADICIO import twin got it with a Cloudflare quick tunnel and twice on Vercel. A request-logging `middleware.js` on Vercel recorded zero requests from GHL, and the live control `www.adicio.com.ar` failed the same way. So the checker failed before fetching anything: the Beta or the account is at fault, not the page. Before changing hosting, log incoming requests and try a control URL in the same dialog. Next steps, in order: «Start from a URL» in a Funnel step; then Funnel & Website AI «Import from a Link or Image»; then a support ticket with the log as evidence.
- [hipótesis] Unknown until measured: which user agent and IP the checker uses when it works; ids/classes kept, JS executed, images copied to Media, global colours/fonts created.

## What is editable without code
- [oficial] Headline tag H1-H6 chosen from the element toolbar.
- [oficial] Global Custom Colors are two-way synced (help 155000006500); Design Kit and Brand Board colours are not. Heading and body fonts are set per page. Per-level H1/H2 global styles exist in Brand Boards, announced «soon» for Funnels/Sites.
- [oficial] Native animations: entrance, loop, button hover; triggered on view; off on mobile by default. No real parallax or scroll-linked animation.
- [oficial] Custom Values work in headlines and paragraphs; [reportado] also inside Custom Code (untested).

## Code hooks
- [oficial] Page CSS, Custom JS/HTML element, tracking code per page and per site/funnel (head/body).
- [oficial] Event `hydrationDone` (help 155000002421) fires when the preview finished hydrating, to run custom code after it.
- [oficial] «Custom Class» field per element (help 155000005422). No custom-id field found. No per-element CSS [reportado].
- [probado] Published pages arrive as server-rendered HTML (Nuxt/Vue) with real `<h1>`/`<h2>`; element ids look like `heading-XXXX` inside `c-heading c-wrapper`; the preview JS dispatches `popup-opened`.
- [oficial] Help 155000006268: «Optimize JavaScript may need to be disabled when critical custom code must run immediately on page load.»
- [oficial] Media library lists CSS and JSON among allowed types, not JS: host the JS on jsDelivr with a pinned version (`@x.y.z` tag; `latest` aliases are cached 7 days).

## Page paths (nested URLs, Beta)
- [oficial] Help 155000005651 «Nested URL Paths Support Guide» (hosted on help.leadconnectorhq.com; the help.gohighlevel.com address 404s; modified 1 Sep 2026): page paths of sites, funnels, stores and webinars may contain `/` (before, slashes became hyphens). Reserved: `/b/`, `/c/`, `/product/`, `/collections/`, `/post/`, `/category/`, `/author/`, `/tag/`, `/store/account`. No trailing slash, no `//`.
- [reportado: Nacho's screenshot 24/11] The «New website page» dialog shows «Ruta» (nested, Beta) next to «Start from a URL».
- [hipótesis] Whether a path or a redirect source may end in `.html`. When a GHL site replaces a static `.html` site, map every old URL to a new path and 301 it (official API redirect endpoints, scope `funnels/redirect.write`). ADICIO draft: `31-adicio-home-ghl/RUTAS-GHL.md`.

See `community-repos.md` for what public repos already solved (and which of those use the internal API).

## Translator findings (measured 24/11, `39-traductor-ghl/INFORME.md`)
- [medido] GHL-published page: only `div` (0 header/nav/main/section/footer/article), 3 width bands (≤767, 768–1024, ≥1025), rows `.inner{max-width:1170px}`, `c-nested-column` exists, native animations are animate.css classes. ADICIO home: 913 KB HTML, 373 KB CSS.
- [código público, NickBhai L113–346] Page JSON is flat per section (rows, cols, elements linked by `child` ids); styles live in fields and render through each section's `general.sectionStyles` CSS keyed by element id; font size is two fixed numbers (`desktopFontSize`/`mobileFontSize`); picker colours must be in `general.colors` as `var(--label)`.
- Design source pages in GHL shape (rows/columns, 3 bands, `.anim-*` hooks) instead of translating arbitrary HTML; decorative CSS goes global by Custom Class, never by GHL id.

## Published-page facts measured read-only (24/11, gohighlevel.com pages + ADICIO preview)
- [probado] Custom Class lands on the `.text-output` div for headings/paragraphs (inside: `<div><h1>`), and on the outer wrapper for columns/rows. Animation layers must target `.cls h1, .cls p`, not `.cls` alone.
- [probado] Hydration can replace nodes or remove injected children when a section nears the viewport. A class or split heading surviving on another page, or an initial `hydrationDone`, does not establish this page's lifecycle. Compare node identity and attached decorations before and after scrolling each section into view.
- [probado] `position: sticky` via custom class works inside a GHL row (conversation-ai `.why-sticky-col`).
- [probado] GHL's own conversation-ai page runs GSAP + ScrollTrigger and listens to `hydrationDone`; native animation is animate.css via `data-animation-class`.
- [probado] `files.leadconnectorhq.com` sends `access-control-allow-origin: *`, so a layer can `fetch` an uploaded SVG. SVG uploads are allowed for Sites (help 48001216629).
- [probado] Menu anchors are not `href="#…"`: buttons use action `scroll-to-element` with the section id. Brand palette ships as `--brand-*` vars in `:root`; page data has its own `schemaMarkup` field and `fontsToLoad`/`customFonts`.
- [probado] Native heading edits can survive Save and reopen with the element-level animation class intact. Verify this on the target draft; it does not establish that classes nested inside TipTap text survive.

## What survives editing (read from the public builder bundle, 24/11)
- [probado] Element-level Custom Class lives in `extra.customClass.value` (array) outside the text; 421 elements on 11 GHL-built Sites pages use it. It survives edits.
- [probado] Text is edited with TipTap: links keep only href/target/rel, headings only their level, spans only style color/font-family/font-size, plus text-align and basic marks. Any class/id/data-* inside text HTML has no schema slot; 0 of 817 GHL texts carry an inner class.
- [hipótesis, from code] The builder parses text on mount but writes back only on onUpdate, so inner classes survive until someone edits that block, then the whole block loses them. Put every animation hook on the element (customClass) and split words in JS at runtime, never in the saved text.

## Schema markup modal (probado 24/11, ADICIO 2)
- SEO panel → «Marcado de esquema» → «Nuevo esquema» → «Añadir esquema» → «Vista JSON». The JSON view holds the WHOLE set as `<script type="application/ld+json">{"@context","@graph":[...]}</script>`; whatever you paste replaces every active schema, so always paste the full graph.
- Validator rejects with «Se ha encontrado un problema en el script JSON» when a node lacks a field it expects (WebSite without `url`). Bisect by node. Use absolute `@id`s. Plain JSON without the script wrapper is rejected too.
- Synthetic `.click()` does not open the dialog; real CDP mouse events do.

## Automation and handoff
- [oficial] API v3 funnels service: 7 endpoints (list funnels, list/count pages, 4 redirect endpoints); Private Integration Token works; the official MCP exposes the same 7. A website is a funnel internally.
- [reportado + public code] Repos reverse-engineered the editor's page JSON and write native pages through the internal API; reported issues: script-made sections render oddly in the editor, the editor overrides fonts, loose colours do not appear in the picker. Forbidden by the terms.
- [reportado] Chrome cloner extensions only copy pages already in GHL. No HTML→GHL or Figma→GHL converter that produces native elements was found in the first pass (29-ghl-paginas); the wider survey (`38-repos-ghl/`) lists candidates whose READMEs claim page writing or HTML conversion. Re-check this line against its `SINTESIS.md` before repeating it.
- [oficial] Share link (funnels) and snapshots (sites and funnels) move native pages between accounts; forms need reconnecting; GHL does not export a page to a file.
- [oficial] AI Studio has a code editor and Git Sync, but its projects cannot be moved into Sites or Funnels. Help 155000007587 (mod. 10 Nov 2026), FAQ: «Can I move or copy an AI Studio project into Funnels or Websites under Sites? No.» It publishes on its own, with a preview URL and a custom domain (Settings → Domains → Connect a domain → AI Studio).
- [oficial] Git Sync (help 155000009214, mod. 21 Oct 2026) creates a private GitHub repo with Automatic Push and Automatic Pull. Every commit on the branch becomes a new project version, for React (Vite) and TanStack Start projects. So hand-written code can enter AI Studio by committing to that repo. [hipótesis] Untested whether a page built outside keeps working there.
- [oficial] Visual Edits (help 155000007914): in the live preview, double-click text to type, and change buttons, images, alt text, icons, colours and spacing. No AI tokens are used. This is AI Studio's way for a client to edit text, not the Sites builder.
- [oficial] Import from image lives inside the builder, not in a separate dialog (help 155000006713, mod. 8 Oct 2026). Open the page in the builder → **Ask AI** (✦, top-left toolbar) → **Build** tab → **paperclip** at the bottom-left of the chat box → attach the image and prompt. A link can also go into that chat. Another way in: Sites → Funnels/Websites → **Build with AI (Beta)**, next to «+ New». The help says it is a reference, not an exact clone, and that the result stays editable with the normal builder controls. Its «Add a new section» does not regenerate the rest, so feed one section screenshot per message. A full-page screenshot gets downscaled and the text becomes illegible.
- [oficial] Terms of service (June 2026, re-read 24/11). Exhibit A «Code of Conduct» forbids «any robot, spider or other automatic device, process or means to access the Platform for any purpose, including monitoring or copying». Customer duty (ix) forbids reverse engineering «the … underlying structure». The penalty for a prohibited use is to «suspend or terminate your **Platform Account**», which is the agency account with every sub-account under it. A test *sub-account* therefore does not isolate the risk; that takes a separate GHL account. The official API is allowed separately, under «API and Marketplace Use».
- [oficial] Creator Studio (help 155000009550) makes social posts, ads, flyers, images and short videos, not web pages. When Nacho says «Creator Studio» about pages, he likely means AI Studio.

## Animation-layer contract
- One bundle (GSAP + ScrollTrigger + SplitText + Lenis ≈ 52 KB gzip; GSAP is 100 % free incl. commercial use and all plugins [oficial, gsap.com/pricing]).
- Loader in the site/funnel Body tracking code (survives page cloning); fallback: a Custom Code block on the page [reportado: GSAP from the header sometimes fails].
- Bootstrap once with `DOMContentLoaded`/`hydrationDone`; never hide content waiting for JS. Keep keyboard-operable widgets functional when animation libraries fail or `prefers-reduced-motion` is active.
- Hook by `anim-*` Custom Class, not GHL ids. For late-rendered sections, debounce a `MutationObserver` on child changes. Track live nodes with a `WeakSet` **per effect**, not one shared set: a button can both reveal and respond to the pointer. Detect missing injected decorations separately: GHL can remove a child while retaining its parent. Reapply static decorations independently of GSAP and reduced-motion mode. For a styled suffix on an editable numeric value, decorate only matching plain text; leave existing markup and the running odometer alone. Verify the exact visible value and computed suffix style after scrolling down and back, both with normal and reduced motion. Refresh ScrollTrigger after remounting; give repeated entrance effects an explicit visible end state.
- Probe native widgets before porting interactions. When an editable FAQ renders as a div-based accordion rather than `details/summary`, bind to its live heading/panel structure, prevent double toggling, sync `aria-expanded`/`aria-controls`, and preserve the original duration and easing. Drive click, Enter and Space; sample intermediate height plus fully open/closed states with and without reduced motion. Do not use mount counts as proof of interaction or fidelity.
- Pause smooth scroll on `popup-opened`; forms are iframes: animate the box, not the fields.
- Heavy effects (WebGL, 3D, Lottie) in one small Custom Code block that reads its text and colours from neighbouring native elements or Custom Values.

## Open questions to answer with the probe
Loader from Body tracking code; `hydrationDone` with and without Optimize JS; which node receives the Custom Class on headings, images and sections; Lenis with GHL popups and sticky; Custom Values inside Custom Code; whether Start from URL keeps `anim-*` classes; the size limit of a Custom Code block.
