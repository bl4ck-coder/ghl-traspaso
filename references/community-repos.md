# What public GHL repos already solved (survey 24/11/2026)

Full detail with repo, path, line and quote: `mirror-brain/01-Projects/Hermes/base-2026-11-18/38-repos-ghl/SINTESIS.md` and `informes/grupo-*.json`. Read it before re-investigating any of these.

## Safe to use (official API or native feature)
- Media upload: `POST /medias/upload-file?locationId=` multipart with a Private Integration Token (elitedcs, ghl-agent-field-guide).
- Schema JSON-LD: native "Schema Markup Generator" in the Website & Funnel Builder, saved to `<head>` on publish (official changelog). Test it before writing schema by hand.
- llms.txt: zeon-studio/ghl-llmstxt-generator uploads to Media and adds a 301 via the official redirects API.
- Loader without flash: InvokableApp/shark-pages holds the block at opacity 0 until its CSS lands (3 s fallback).
- Start on `hydrationDone` + 2 s fallback + run-once guard; scope styles under `#ghl-page` with `:where()` resets; use `clientWidth`, not `100vw` (yashcoga/html-to-ghl).
- Builder preview does not substitute Custom Values: verify on the published URL.

## Internal API only (same ToS risk as a custom MCP)
- Native editable pages from code: NickBhai-GH/ghl-internal-api (MIT) and hanifmalik1436/CMO2 build sections→rows→columns→elements and save with `/funnels/builder/autosave`.
- A Site is a funnel with `type:"website"` (uxie doc).
- Colors must be registered in `general.colors` `{label,value}` + `--label` vars; without that list the page returns HTTP 500 even after a 201 save.
- Full width needs `max-width:1170px` rewritten in the compiled `section.general.sectionStyles`; the toggle alone changes nothing.
- Saving onto a page that already has content may never become the visible version; create a new step, retry, and re-read every write. Re-mint ids when copying sections.
- Custom Class lands in `extra.customClass.value`; element ids are random on creation.
- Cloudflare 1010 without UA + `sec-ch-ua` + Referer + Origin; autosave wants `Origin: page-builder.leadconnectorhq.com`.

## Ban risk (checked 24/11/2026)
- No public report found of an account suspended for automating the page builder. Reported suspensions are messaging/spam, billing, Twilio/A2P and Meta.
- Paid cloner extensions that write pages into the builder are sold openly (Super Cloner by AllThingsGHL, GHL Cloner on Chrome/Edge stores, Funnel Cloner Pro, Clone2GHL).
- ToS: suspension at sole discretion; excessive API use can lose API access; a breaching sub-account can escalate to the agency account.
- There is no honest numeric probability. Lowest-exposure order: driving the real editor in the user's own session at human pace < reusing the open builder's own requests (Clone2GHL style) < a script calling the internal API with copied tokens.
- The bigger practical risk is overwriting a live page (saves onto pages with content may not publish); always build on a new blank page.

## Nobody solved
"Start from a URL" failing, Ask AI exact clone, GSAP/ScrollTrigger/Lenis on native elements (0 code hits), Lenis with popups/sticky, nested paths, editable text inside code blocks, global styles per heading level, ToS exposure.
