# Prompts for Ask AI → Build (import from image into Sites)

Tool: `31-adicio-home-ghl/para-ghl-imagen/armar_prompts.py` (run with `uv run -q --with beautifulsoup4`). It reads the page's `importar.html` and writes one message per section (`prompts/NN-*.txt` + `PROMPTS-ASK-AI.md`). Reuse it for any page: change `GRUPOS` (output name, screenshots to attach, section ids, layout/background line) and `BASE` (public URL of the media).

## Rules that go in every prompt (why)
- Exact text between « », letter by letter; the screenshot is for design only. Why: the image model rewrites or summarises text it reads off a screenshot.
- Mark each heading level ([H1]/[H2]/[H3]) and say there is one H1; small uppercase labels are Paragraph. Why: SEO, and Ask AI picks levels by size.
- Only native elements, no code/HTML blocks. Why: editable = native.
- Image and icon URLs with alt text; no stock, no generated images.
- Global colours with names + Google fonts + radius/shadow/button specs, from the page's CSS variables.
- No animations: they come later from the Body layer + Custom Class.
- Mobile: one column, same order.
- "No me hagas preguntas: construí directamente."
- First message carries all rules; the rest say "add below the last section, do not change previous ones".

## Before handing it over
- Cross-check: every «text» in the prompts must exist in the page's visible text/alt/placeholder (ADICIO 24/11: 141 quotes, 0 missing), every H1/H2/H3 of the page must appear, exactly one [H1].
- Use `get_text('')` and turn `<br>` into spaces, otherwise BeautifulSoup inserts fake spaces ("Liboreiro ,", "20 +").
- Media URLs point to the temporary public deploy: do not delete it until GHL has copied the images to its Media.

## After each message
Send only message 1 first, get the preview link, measure with `C/comparar.py` and `verificar_seo.py`, then continue. Correction messages (text, heading level, extra element) are in the same file.

Unverified (24/11): whether Ask AI has a character limit per message (largest prompt ~5 KB), whether it hot-links or copies image URLs, and how faithful it is to the given text.