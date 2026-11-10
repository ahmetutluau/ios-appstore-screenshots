# Figma reference library: 17 community App Store screenshot kits

A curated set of free Figma Community kits, studied in November 2026. This repo only links to them; their designs belong to their authors.
Use this file to **pick a look before rendering** and to **vary the look** across apps, so each
set does not look the same as the last. Each kit lists its signature moves, a compose.py recipe (v3 keys),
and how to rebuild it in Figma.

> Access note: the Figma MCP can only read files you can **edit**. Community files return
> "you don't have edit access". To use a kit directly in Figma mode, open the link, click
> **Open in Figma / Duplicate** (it lands in Drafts), and give Claude the new link.
> Without duplicating, use the recipes below because they reproduce the look.

## 0. Quick picker (family → kits → compose.py start file)

| Family | Looks like | Kits | Start from |
|---|---|---|---|
| **Bold flat** | solid saturated colour per frame, left heavy headline, big/tilted phone, stickers, people cut-outs | #7 AppLaunchpad, #12 Aweb, #10/#11 BRIX, #3 L. Tobolski | `examples/bold-flat.json` |
| **Marker / playful** | light flat bg, black heavy centred headline, highlighter keyword, giant number, laurel hero, sticker text | #2 ASO.dev | `examples/marker.json` |
| **Mono editorial** | charcoal gradient, thin light title, realistic phone, numbers, diagonal band | #16 const lab, #13 Farhan Shakir | `examples/mono.json` |
| **Soft 3D** | warm solid + glossy spheres, ALL-CAPS headline, white-bezel phone | #17 Arzu Cetinkaya | `examples/soft-3d.json` |
| **Fintech clean** | vivid flat colour per frame, left semibold 2-liner, underlined keyword, dot grid, sparkle | #15 FREE templates, #14 12-scene kit | `examples/fintech.json` |
| **Glass AI** | pale blue mesh, left navy headline, frameless glowing screen, floating cards; navy mirror frame | #5 BRIX Agency AI | `examples/glass-ai.json` |
| **Caption bottom** | phone hangs from top edge, title + subtitle under it, geometric decor | #3, #8 jello, #14, #17 last frames | `examples/caption-bottom.json` |
| **Panorama** | one picture across frames: phone crossing a seam, blobs, bands | #9 500+, #8, #13, #6, #4 | `examples/panorama-split.json` |
| **Aurora / dark 3D** | near-black, gradient headline, 3D chrome objects, tilted phones | #6 270+ screens kit | `examples/aurora.json` + 3D decor PNGs |
| **Colour-system grid** | one layout × 6 colourways (light, vivid, dark), outline bezel tinted to the bg | #1 Appstore & Google Play kit | `examples/aurora.json` / `classic` + `device.color` |

**Variety formula:** family × layout (`text_pos` top/bottom, panorama) × device treatment
(frame / white bezel / frameless / tilt / fan / crossing seam) × one extra (pop-out, number, badge, laurel,
pattern). Change at least two axes between two apps of the same category.

---

## 1. Appstore and Google Play Screenshot Templates
https://www.figma.com/design/rgG1Sq1GJJ6b7vWUmVIY40/?node-id=135-767
- **Look:** one centred layout in 4 colour systems: *light pastel* (bg tint + phone outline in the same
  hue), *vivid gradient* (blue/teal/green/red/magenta/amber + white phone), *dark* (navy/teal/forest/
  maroon/black + coloured outline), *dark gradient*. Small app icon above "Add headline", 2-line sub,
  phone bleeding off the bottom. Cover also shows a laurel "8 000+ people liked our app", tilted phones,
  photo-backed frames (portrait photo filling the top half), and a cream bg with a dark headline.
- **compose.py:** `theme: classic`, `background: linear`, `device: {"color": "<dark hue>", "rim": "<hue>", "bezel": 0.014}`
  for the tinted thin outline. Run one config per colourway to give the user a choice.
- **Figma:** frame fill gradient (2 stops), phone = rounded rect stroke 6px in hue, screen image fill.

## 2. App Store Screenshot Creator by ASO.Dev
https://www.figma.com/design/P1HgDJd1yaHjYVKOuHQLJe/?node-id=133-771
- **Look:** 6.9" (1290×2796) light-blue frames. Hero = no phone: "APP NAME" black heavy, pink laurel
  with "#1" + small text, a skewed black sticker with pink/white stacked "TEXT TEXT!". Feature frames:
  black heavy centred headline with a **yellow highlighter** behind 1-2 words, a **giant white
  numeral** (1, 2...) behind the phone, "Powered by" footer. The cover shows a phone stack with stickers
  ("HEY!", "NEW", "WOW!") and wavy line patterns.
- **compose.py:** `theme: marker`, `decor: [{"text": "01", "size": 0.95, "color": "<lighter bg>"}]`,
  sticker = `{"badge": "...", "shape": "tag", "color": "#111", "text_color": "#FF4FA3", "rotate": -6}`,
  laurel = `rating` with `"stars": false` and a REAL value only.
- **Figma:** highlighter = rectangle behind the word (fill #FFE04A, radius 8). Numeral = text layer
  Montserrat Black 1400px, white 70%, under the device.

## 3. App Store Templates (Lauren Tobolski)
https://www.figma.com/design/ZDpkAt25nyhcF1rtk6y6V4/?node-id=1-334
- **Look:** 8 themed rows × 6 frames: Grey, White, Abstract, Solid dark, Light blue, Orange, Yellow,
  Purple. Frame 1 = **text-only hero** (icon + "App name goes here", left aligned). Others alternate
  **caption top / caption bottom**, upright or 30° tilted phones, diagonal white bands, geometric decor
  (outline hexagons, circles, chevrons `<<<`, zig-zags).
- **compose.py:** `text_pos: "bottom"` on alternate frames, `decor` shapes `hexagon` / `ring` / `chevrons`,
  `pattern: {"type": "band"}`, hero frame `device: {"style": "none"}` + `headline_style.align: left`.
- **Figma:** decor = polygon tool, stroke 8px white, no fill.

## 4. Google Play & App Store Template – Auto Layout Mockups
https://www.figma.com/design/dL41NeopYSxmqJ3CpZ0t0h/?node-id=7-28
- **Look:** a workflow idea more than a style: you replace the screenshot **once** in a "Replace here"
  row and every mockup updates (components). Rows show upright phones, mixed tilts (±8-15°) and
  phones crossing frame seams on a light blue bg.
- **Use:** in Figma mode, build `Screen/<n>` components holding the raw screenshots and use instances
  inside every device, so localisation = swap 1 component per screen. In compose.py the same thing is
  one `screenshot` path per frame.

## 5. App Store Screenshots Figma Template | BRIX Agency (AI chat)
https://www.figma.com/design/41USxnL7w0LpTfqPQUT5nB/?node-id=7970-148
- **Look:** sections "Welcome Screens", "Main Features". Pale blue→white gradients, logo top-left, left
  or centred navy headline with blue keyword, frameless phone with soft glow, **lifestyle photo** frame
  (person holding the phone), 3D glass hand, glowing orb, floating chat/UI cards; mirrored deep-navy
  variants of every frame.
- **compose.py:** `theme: glass-ai`, pop-outs for the chat bubble, last frame `background: aurora` navy.
  Lifestyle photo frame: `device: {"style": "none"}` + photo as `decor` image (user-supplied, licensed).
- **Figma:** bg linear #E9F0FF→#FFFFFF, orb = ellipse radial gradient + layer blur 40.

## 6. App Store and Play Store Screenshot Template (270+ screens)
https://www.figma.com/design/UAh19gYey0HILk4ARFaui1/?node-id=0-1
- **Look:** dark (near-black, deep purple, forest green) presentations, **gradient headline** (violet→blue),
  left-aligned two-tone ("Change the way / **You money**" with line 2 in accent), 3D chrome blobs and glass
  cubes, tilted phones, 3D character for fitness ("30 DAYS FITNESS CHALLENGE" pink), laurel "10 million people",
  green "Place your **heading**". Some sets are panoramas whose phone rows form a "comb" across frames.
- **compose.py:** `theme: aurora` + `headline_style.align: left`, `highlight: gradient`,
  3D objects as transparent PNG `decor` (generate in Figma `generate_image` or supply).

## 7. Free App Store & Play Store Screenshot Template (AppLaunchpad)
https://www.figma.com/design/QOVu3QR8SWqT0HLvU3BdCu/?node-id=53-171
- **Look:** loud flat colours (green, purple, red, yellow, teal, pink) with **people cut-outs** overlapping
  the phone, hand holding phone, rotated stickers ("Editor's choice", "40% OFF" starburst, "App of the
  day"), heavy 2-3 line headline top-left, phones tilted 10-20° in collages. Sets for iPhone, iPad, Android.
- **compose.py:** `theme: bold-flat`, `badge` decor (`starburst` / `circle`), cut-out = `decor` image with
  `layer: front`. Only use award stickers that are REAL.

## 8. iOS App Store Screenshot Preview Template (madewithjello)
https://www.figma.com/design/lF7lNdNAqGT26XBuj8Un67/?node-id=7-1244
- **Look:** pastel/gradient frames (peach, lilac, mint, yellow, blue, teal), **caption at the bottom** on
  some frames, **one phone split across two frames**, a **fan of 4 phones** ("Editors' Choice"), a
  **before/after split screen** with a slider knob ("Go Dark..."), a laurel at the bottom.
- **compose.py:** fan = `devices: [{"at": [0.36, 0.1], "tilt": 16}, {"at": [0.64, 0.1], "tilt": -16}]`
  behind the main phone; split across frames = `panorama: true` + `panorama_devices` at x = 1.0.
- **Figma:** split = place one device over the seam of two clip-content frames.

## 9. 500+ App store screenshot templates (Android & iOS)
https://www.figma.com/design/AbV7Li8ZmU6y8e2gKkzrdR/
- **Look:** 27 panorama sets (8 frames each) on deep blue / purple / black / teal / yellow with **big organic
  blobs and circles crossing seams**, a **giant phone spanning two frames**, rotated phones at seams, tiny
  left-aligned headline + sub at the top. Strong swipe continuity.
- **compose.py:** `panorama: true`, `panorama_decor: [{"shape": "blob", "size": 1.3, "at": [1.0, 0.78]}]`,
  `panorama_devices`. Keep headlines short (size 0.07) so the art carries the frame.

## 10 & 11. App Store Screenshot Templates | BRIX Template
https://www.figma.com/design/4qhQ1t6wZuvDbLODfMTeRr/?node-id=1867-1095 ·
https://www.figma.com/design/rJr6MHVjRaaP0i0OVpn42U/?node-id=1855-473
- **Look:** electric indigo (#4F46E5-ish) solid frames, left-aligned white headline + sub, phones with a
  **thick white rounded bezel**, tilted 15-30° and overlapping into the next frame; an App Store listing
  simulator (light + dark) to preview the strip in context.
- **compose.py:** `theme: bold-flat`, `device: {"color": "#FFFFFF", "rim": "#E6E6EA", "bezel": 0.045}`,
  `tilt` on alternating frames. Always review with `showcase.png` as the "listing preview".

## 12. App Store & Play Market screenshots template (Aweb)
https://www.figma.com/design/1mm3FWKvHte6wG6mqWNhs2/?node-id=5-125
- **Look:** 3 variants × 6: **royal blue** with white swirl line + laurel "8 000+ people liked our app";
  **black** with wavy line art; **white/cream** with orange accent and peach **topographic contour**
  pattern + diagonal phone bleeding off the corner. Big left-aligned headline, secondary text below.
- **compose.py:** `theme: bold-flat`, `pattern: {"type": "contours"}`, `decor: [{"shape": "wave"}]`,
  `device.tilt: -20` with `x: 0.15` for the corner bleed.

## 13. App Store Preview/Screenshots Template (Farhan Shakir)
https://www.figma.com/design/KeC2KMhZkXRQ0xER1NVoQC/?node-id=0-1
- **Look:** charcoal panorama with a **beige diagonal band** running through all frames, logo + tagline
  frame, 3 fanned phones with huge numerals on screen, check-mark tags ("✓ Easy To Use",
  "✓ Creative Design"), tilted phones crossing seams. Also covers app icon and feature graphic.
- **compose.py:** `theme: mono`, `panorama: true`, `pattern: {"type": "band", "color": "#8C8778"}`,
  `eyebrow` + `eyebrow_icon: "check"` + `eyebrow_solid: true`.

## 14. App Store Screenshot Template (12 scenes / 72 screens)
https://www.figma.com/design/Ad9vRSEKEqyw3cxIerW7hM/?node-id=0-1
- **Look:** 12 scene styles: black, multicolour stripes, beige photo, blue-glass, blue diagonal
  wedge, pastel, iridescent gradient phones, white with colour stripe base, mint "Best of the App Store"
  laurel, white **caption-under-phone** ("A super helpful app feature goes here"), accent underline bar
  under the headline.
- **compose.py:** mix of `classic`, `fintech`, `text_pos: bottom`; wedge = `pattern: {"type": "band", "angle": -60}`.

## 15. FREE App Store Screenshot Templates
https://www.figma.com/design/o0q3dgfsM6fqqfQ2sPefSk/?node-id=1-29
- **Look:** Style 01 = one vivid violet with alternating caption top/bottom; Style 02 = a different flat
  colour per frame (violet, blue, orange, red, green, teal). Left-aligned 2-line semibold headline with an
  **underlined keyword** ("**Manage** money as a team", "Pay anyone **instantly**"), small sub, sparkle icon,
  **dot-grid texture**, a teal→red gradient frame, a lime frame with dark text.
- **compose.py:** `theme: fintech` (exactly this), per-frame `bg`, one dark frame with `text_pos: bottom`.

## 16. Template for App Store Screenshots (const lab)
https://www.figma.com/design/0e2jQJBWALSLLYELun27d2/?node-id=5-13
- **Look:** grey gradient, thin light title + small description, an **isometric phone lying across
  frames 1-2**, a realistic black phone, a **magnifier lens** enlarging a detail (6 in a circle), language
  flags for "multilingual", App Store listing mock to preview.
- **compose.py:** `theme: mono`, `panorama_devices` with tilt ~60°, a lens = `popouts` with a
  square-pixel `crop`, `radius: 0.5` (renders as a circle) + `scale: 1.6`, flags = `decor` emoji.

## 17. App Store & Play Store Screenshots Template (Arzu Cetinkaya)
https://www.figma.com/design/Ne5l77qtuZitfiTSJ75x26/?node-id=0-1
- **Look:** orange #F0913A, **glossy 3D spheres** (bokeh), ALL-CAPS white "WRITE YOUR TEXT HERE",
  white-bezel phones; the last 3 frames tilt the phone across the seam with the caption at the bottom.
- **compose.py:** `theme: soft-3d` (spheres are part of the preset), `text_pos: bottom` on the last frames.

---

## Rules learned from all 17
1. **Alignment is a style choice.** Left-aligned headlines (#5, #6, #7, #10-12, #15) read modern
   and editorial. Centred headlines (#1, #2, #8, #16, #17) read calm and classic. Never mix them in one set.
2. **Caption position alternation** (top ↔ bottom) gives rhythm without changing colours (#3, #8, #15).
3. **One colour per frame** works when the layout is constant (#7, #15). With one colour for the whole
   set, vary the light, decor or tilt instead (#2, #16).
4. **Continuity sells the swipe.** Something should cross at least one seam: a phone, a blob or a band (#8, #9, #13, #16).
5. **Hero frame without a phone** is common (#2, #3, #13): brand + promise + one real proof element.
6. **Stickers and badges** go on at most 1-2 frames, rotated 6-15°, never over key UI.
7. Every award, laurel or user count must be **real**. Template text like "8 000+ people", "#1",
   "Editors' Choice" is a placeholder, not a claim to copy.
