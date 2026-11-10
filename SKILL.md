---
name: "ios-appstore-screenshots"
description: "Create App Store marketing screenshots for native Swift/SwiftUI iOS apps, as an editable Figma file (preferred) or with Pillow only (no API keys). Includes 11 style presets distilled from 17 professional Figma kits, so every app gets a different, professional look."
---

# iOS App Store Screenshots (native Swift/SwiftUI, no API keys)

Produces modern, captioned App Store screenshots: layered brand background (aurora glow, mesh,
gradient), two-tone headline, the real simulator screenshot in a frame / frameless / glass device,
plus modern extras (pop-out UI cards, eyebrow, chips, rating laurel, decor, panorama).
**Design guide with every pattern, config key and Figma recipe: `references/design-patterns.md` -
read it before step 3.5.** **Style library: `references/figma-examples.md`** - 17 professional Figma
community kits (links, signature moves, compose.py recipe, Figma recipe) grouped into families.
Use it to choose and vary the look.

Two output modes (steps 0-3 are shared):
- **Figma mode (default when the Figma MCP is available)** - step 4F. Editable Figma file:
  real text layers, a reusable template, one page per locale, realistic device frame.
- **Pillow mode** - step 4. Fast, deterministic PNGs with a drawn frame; good for quick
  drafts or when Figma is not connected.
Google Flow / Gemini (step 6) is NOT needed in Figma mode; offer it only for lifestyle
scenes (hand holding phone, desk shots) or to polish Pillow output.

## Workflow

### 0. Brand
Ask for (or read from the asset catalog `AccentColor` / `Assets.xcassets`) the brand colours:
`bg`, optional `bg2` for a gradient, `text`, and an `accent` for highlighted words.
Accent must contrast with bg (check WCAG >= 3:1 for large text).

### 1. Benefit discovery
Read the Swift sources (Views, Models, the onboarding/paywall copy, `Info.plist`, existing
App Store description if present). Draft **3-6 benefits**, ordered:
1. The magic moment (the thing competitors do not do).
2. Daily-use proof (core loop screen).
3. Trust / control (data, privacy, sync, widgets...).
4+. Supporting features.

Headlines: **<= 6 words, start with a verb, user benefit not feature name**
("Track every habit in seconds", not "Habit list view"). Write them as **two lines** split with
`\n`: line 1 the setup, line 2 the payoff ("Hum it.\nWe'll finish it.") - modern themes colour or
lighten line 2. Pick 1-2 words as `highlight`. Optional `sub` <= 6 words, optional `eyebrow`
(1-2 word category label). Confirm the list with the user before continuing.
If the app has localizations, ask which locales to produce.

### 2. Capture raw screenshots (on the user's Mac)
Give the user these commands (iPhone 16 Pro Max / 17 Pro Max simulator = 6.9", 1320x2868):

```bash
xcrun simctl boot "iPhone 16 Pro Max"   # or the 17 Pro Max name in their Xcode
xcrun simctl status_bar booted override --time "9:41" --batteryState charged \
  --batteryLevel 100 --cellularBars 4 --wifiBars 3 --dataNetwork wifi
# navigate to each screen, then:
xcrun simctl io booted screenshot raw/01.png
```
Tips: seed realistic demo data (a `-UITestDemoData` launch argument or a debug seed),
light mode, no PII, no real brand/bank names, no placeholder "Lorem". For many screens
or locales, suggest an XCUITest that navigates and calls `XCUIScreen.main.screenshot()`
(launch with `-AppleLanguages (de) -AppleLocale de_DE` per locale).

### 3. Rate & pair
Read each raw screenshot. Rate **Great / Usable / Retake** (Retake if: empty states,
spinners, debug UI, keyboard covering content, cropped dialogs, dark mode mixed with light).
Pair each benefit with its best screenshot; coach retakes concretely.

### 3.5 Art direction (do not skip - this is what makes it look modern)
Read `references/design-patterns.md`. Then:
1. Read `references/figma-examples.md` §0 (family picker). Pick **2-3 candidate families** that fit the
   brand (themes: `classic`, `aurora`, `sunset`, `duotone`, `light-pop`, `bold-flat`, `marker`, `mono`,
   `soft-3d`, `fintech`, `glass-ai`; layouts: `text_pos: bottom`, `panorama`). Start each from its
   `examples/<family>.json`, render frames 1-2 (`--only 1`, `--only 2`), show them side by side, and
   let the user choose. Name the reference kit ("BRIX-style bold flat") so the user can open it.
   **Variety:** when the user makes many sets, or makes another set for a similar app, change at least
   two axes (family, alignment, caption position, device treatment, extra). Avoid repeating the
   previous set's combination; record the combination you used in the project's `config.json` `_ref` key.
2. Plan the set as a story: frame 1 **hero** (logo/wordmark + promise, rating only if real),
   frame 2 magic moment with a **pop-out**, then core loop (chips), trust, support.
3. Give each frame at most ONE extra (pop-out / chips / rating / decor / badge / numeral). Use tilt on
   at most 1-2 frames (bold-flat and panorama sets may use more). Something should cross a seam at least once
   (`panorama_devices`, a blob or a band) - the Figma kits all use swipe continuity.
4. Never invent social proof: ratings, user counts, awards must be real and current (App Store
   guideline 2.3.7 / misleading claims). No emoji inside headlines (font has no colour glyphs).

### 4. Pillow mode - compose
Copy `scripts/compose.py` from this skill's folder next to the raw folder, write a
`config.json` (start from `examples/<theme>.json`; `examples/config.json` is the minimal v1
format, still supported), then:
```bash
pip install Pillow   # if missing
python3 compose.py config.json
```
Sizes: `1320x2868` (6.9", required). Add `1242x2688` (6.5") only if the user wants it;
`2064x2752` for iPad 13" only if the app supports iPad and has iPad raw shots.
`python3 compose.py --themes` lists presets (11). Iterate per frame with `--only N`.
Device bleeds off the bottom by default (`device.fit: "full"` keeps it whole); phone tops are
aligned across frames (`device.sync`). Pop-out crops are fractions of the raw screenshot - read
the raw image to find card/row edges, never cut through text.
Fonts by role (`heavy`, `bold`, `light`, `serif`, `rounded`...): SF Pro Display / New York /
SF Pro Rounded if installed, else Inter / Georgia / DejaVu; override with `"fonts": {role: path}`.
Turkish: set `"locale": "tr"` (correct İ in caps). For CJK/Arabic/Thai set fonts that cover
the script (e.g. Noto Sans CJK) or glyphs render as boxes.

### 4F. Figma mode
MANDATORY: load the `/figma-use` skill before any `use_figma` call, and call
`create_session` once the file key is known.

**Starting from a reference kit (fastest professional result):** the 17 kits in
`references/figma-examples.md` are Community files; the Figma MCP cannot read or edit them
("no edit access") until the user opens the link and clicks **Open in Figma / Duplicate**. Ask the
user to duplicate the chosen kit, then `create_session` on the duplicate's key, `get_metadata` to find
its frames/components, and replace the screens and texts. Otherwise rebuild the look from the kit's
Figma recipe in that file.

**Template (first time only, or reuse the user's existing template file - ask):**
1. `create_new_file` named `<App> - App Store Screenshots`; page `Template`.
2. Component `Device/iPhone 6.9`: prefer a realistic iPhone 16/17 Pro frame the user
   already has (Apple Design Resources or a Community mockup - ask, or
   `search_design_system`); otherwise build one: rounded rect bezel #121214 (radius ~14%
   of width, bezel ~3.5%), inner screen rectangle with image fill + matching inner radius,
   Dynamic Island pill.
3. Component `Screenshot/6.9` = frame **1320x2868**, clip content, layers named exactly:
   `bg` (solid or linear gradient from brand colours), `headline` (text, Inter Black /
   Montserrat ExtraBold, ~116px, centred, line-height 112%, max 3 lines, width 1136),
   `sub` (optional, ~48px, 80% opacity), `device` (instance of the device component,
   width ~1110, top ~y 620; for the bleed layout let it run off the bottom).
   Use variables/styles for `bg`, `text`, `accent` so a brand change is one edit.

**Modern layers (build them per the Figma recipes in `references/design-patterns.md` §4 and the
per-kit recipes in `references/figma-examples.md`):**
aurora/mesh background (blurred ellipses), glow behind the device, two-tone headline via
ranged fills, eyebrow pill, frameless or glass device, pop-out cards (image fill CROP of the
screenshot, 115%, shadow), optional tilt, rating laurel, decor, panorama ring across seams.
Fonts: SF Pro does NOT render server-side through the MCP - use Montserrat/Inter/Poppins
(serif: Playfair Display / DM Serif Display).

**Per app / locale:**
1. `upload_assets` the raw simulator screenshots.
2. Page `en-US` (one page per locale): one `Screenshot/6.9` instance per benefit, named
   `01-<slug>`, `02-<slug>`... laid out left to right, 100px gap.
3. Set `headline` text; colour the `highlight` words with the accent via ranged text
   fills. Set the screenshot as the device screen's image fill (FILL scale).
4. `get_screenshot` each frame and review it yourself (same checks as step 5).
5. Localization: duplicate the page, rename to the locale, replace only text and screen
   images. For CJK/Arabic/Thai switch the headline font to one that covers the script.
6. Optional backgrounds/illustrations: Figma AI image generation (`generate_image`) -
   never over or instead of the app UI.

**Export:** tell the user: select the frames on a page -> Export PNG at 1x -> exact
1320x2868. (Or use `download_assets` if it exports at exact size; verify pixel size.)
If the user also wants PNGs here, receive them and run the step 5 checks.

### 5. Review
Open `showcase.png` (Pillow) or the frame screenshots (Figma) and every frame yourself.
Check: headline <= 3 lines and not touching the phone, highlight colour applied, Dynamic
Island not covering important UI, exact pixel size, first 3 frames tell the pitch alone.
Modern checks: phone tops aligned, pop-outs sit on their source and crop on clean edges, no
more than one extra per frame, decor not over key UI, background light varies between
neighbours, accent used consistently, the set looks good as a swiped strip (showcase.png).
Pillow: iterate with `--only N`.

### 6. Optional: polish in Gemini / Google Flow (manual, no API cost)
Only for Pillow output or lifestyle scenes. Give one prompt per frame to paste into
Gemini or Flow together with the composed PNG, e.g.:
> Keep this exact App Store screenshot layout, headline text, colours and the app UI
> inside the phone pixel-identical. Replace the flat drawn phone with a photorealistic
> iPhone 16 Pro (titanium edge, subtle reflections), soft studio shadow. Do not change,
> translate or re-render any text. Portrait 9:19.5.
Then ask the user to drop the results back; resize/crop to the exact App Store size with
Pillow (cover-fit, centre crop) and **verify the UI text was not altered** - reject any
image where the AI rewrote text or UI.

### 7. Deliver
Pillow: `screenshots/final/<size>/01.png ...`, plus `showcase.png`. Figma: file link +
export instructions. Upload order = file/frame order. If the project uses fastlane, also
copy to `fastlane/screenshots/<locale>/` as `1_*.png`, `2_*.png`.

## Checklist
- [ ] Exact sizes (1320x2868 for 6.9"), PNG/JPG, RGB, no alpha
- [ ] 3-10 frames; frames 1-3 carry the pitch
- [ ] Headlines <= 6 words, consistent tone, no claims the app cannot back up
- [ ] Status bar 9:41, full battery; no PII, no real third-party brands in UI mocks
- [ ] Every locale renders real glyphs (no tofu boxes)
- [ ] Family chosen with the user from `figma-examples.md`; frame 1 is a hero; >= 1 strong extra in frames 1-3
- [ ] One alignment across the set; something crosses a seam at least once
- [ ] Template placeholders ("8 000+ people", "#1", "Editors' Choice") replaced or removed
- [ ] No invented ratings / user counts / awards
