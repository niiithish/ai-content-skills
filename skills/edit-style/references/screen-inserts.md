# Screen inserts: search results, AI answers, a typed address, a product page

Phone and web screens that a line names ("I looked it up", "ChatGPT said", "go to trymysa.store", the study). Approved on Calvin video-23 (DCT#28 reference, 2026-11-09) after four rounds of fixes; these rules are those fixes. Examples: `assets/screens/example-*.jpg`.

## Make them ourselves, never from a screenshot

- **A copy of the UI's style, made by us, with our words**: the right fonts (Google Sans / Google Sans Text, Inter for a chat answer; download them), colours, spacing, dark or light as the reference shows. A crop of a real screenshot showed a cut-off logo and a prompt box, and the user rejected it ("1:1 clone of the UI style… made by us").
- **No brand logos, no prompt or input box, no phone status bar** (a fake iPhone clock and battery "looked shit, i dont have a iphone"). Show the page, not a phone.
- Never name the real app in a Flow prompt; these are HTML pages rendered locally, not generated.
- The text says only what the product page claims, in the brief's words. **No offer or sale banner** unless the user confirms the offer ("dont show the fall sale").

## Make the whole frame the screen

- **Focus screen (the reference's look, the default):** the page zoomed about 2× onto the phrase she is saying, that line sharp and highlighted, a heavy lens blur above and below. The edit pushes it in fast. A flat screenshot on a plain background is "super boring".
- **The key line sits at the frame centre (y 960)**, so a 1:1 Facebook centre crop keeps it.
- **No empty top half.** Above the answer, render what the page really has (search bar with the query, results tabs, filter chips) so the blur has page under it, never a flat fill.
- **A product page scroll** starts under any sale bar, moves slowly with ease in/out, and lands on Add to Cart at frame centre by the end of its slot, then holds ~0.75 s. Time the scroll to the slot length, never a fixed speed ("super fast").
- **A typed address**: a dark, zoomed browser address bar typing the URL, suggestion row under it, no status bar.

## How (keep the sources in the project)

1. Copy a template from `assets/screens/` into `edit/media/screens/src/` (never the scratchpad: video-23's sources were lost with it): `search-ai-overview-dark.html`, `chat-answer-light.html`, `address-bar.html` + `type_address.js` (frames of the typing), `render.js` (renders at 2× so the zoom stays sharp).
   Rendering needs `npm i puppeteer-core` in a scratch folder and `/usr/bin/chromium`; or without node: `chromium --headless --hide-scrollbars --force-device-scale-factor=2 --window-size=540,960 --screenshot=out.png file://…`.
2. Put our text in, add the page header above the answer, and highlight the spoken phrase.
3. Make the focus frame with `talking-head/scripts/dct-28/make_focus_screens.py` (set the focus point and zoom per screen) and the scroll with `make_219_scroll.py` (set the start under the sale bar and the Add to Cart row).
4. Place them like any still (2 %/s push) on the caption start of the phrase they show. Send a frame of each before building on it.
