# Design patterns for modern App Store screenshots

Studied from top-grossing 2025-26 sets (Kling AI, Melodize, Suno, MyTunes, AI Music Generator) and,
for v3, from 17 Figma community kits; see **`figma-examples.md`** for the per-kit catalogue and the
family picker. Each pattern lists what it is, when to use it, the `compose.py` config, and the Figma recipe.

## 0. What separates "modern" from "plain"

| Plain (v1 output) | Modern |
|---|---|
| One flat gradient | Depth: light blobs / aurora glow, grain, a glow behind the phone |
| One headline weight, one colour | **Two-tone headline**: line 1 statement, line 2 the payoff in accent colour, or bold + light |
| Phone sits alone | Something **breaks out of the phone**: an enlarged UI card (pop-out), floating chip, decor |
| Every frame looks identical | Same system, per-frame variation: mirrored light, colour shift, tilt on one frame |
| Frame 1 = another feature | **Frame 1 = hero**: logo/wordmark + promise (+ real rating / social proof) |
| Frames are islands | Optional **panorama**: background element flows across frame seams |

Rules that hold across all five references:
- Headline 2 lines (rarely 3), centred, 7-10% of canvas width in size, very tight leading (1.0-1.1).
- Line 2 carries the benefit and is the coloured or lighter one: "Hum it. / **We'll finish it.**"
- Sub-line is optional, small (~3% W), 70-80% opacity, max 1-2 lines.
- The phone (or bare screen) takes 75-82% of the width and bleeds off the bottom.
- The phone top sits at the same y on every frame (compose.py: `device.sync`, on by default).
- One accent colour, used everywhere: keyword, eyebrow, glow, decor.
- At most one "extra" per frame (pop-out OR rating OR chips OR decor), never all at once.

## 1. Themes (presets in compose.py, `"theme": "<name>"`)

| Theme | Looks like | Use for | Colours to give |
|---|---|---|---|
| `classic` | v1: vertical gradient, framed phone | conservative brands, quick drafts | bg, bg2, accent |
| `aurora` | Kling / Melodize: near-black base, brand-colour light blooms, frameless screen, glow, line 2 in accent | AI, premium, tech, dark-UI apps, and also light-UI apps (the white screen pops) | bg = brand mid tone, bg2 = very dark version, accent = bright tint |
| `sunset` | Suno: vivid warm diagonal gradient, serif headline, glass ring around the phone | creative, lifestyle, music, journaling | bg + bg2 two saturated warm hues, accent #FFFFFF |
| `duotone` | MyTunes: two-colour diagonal (blue to pink), heavy line 1 + light line 2, tilted phone + pop-outs | utilities, productivity, B2B | bg + bg2 contrasting hues |
| `light-pop` | AI Music: pastel mesh, ALL-CAPS heavy headline, gradient or pill keyword, decor | consumer, fun, kids, social | accent + accent2 (gradient), text dark |

v3 families (from the Figma kits, details in `figma-examples.md`):

| Theme | Looks like | Use for |
|---|---|---|
| `bold-flat` | solid saturated colour per frame, LEFT heavy headline, big/tilted framed phone, stickers | consumer, edtech, food, fitness |
| `marker` | light flat bg, black heavy centred headline, yellow highlighter keyword, giant numeral | playful utilities, finance-for-everyone |
| `mono` | charcoal gradient, thin light title, realistic black phone, band / numbers | premium minimal, dev tools, finance |
| `soft-3d` | warm solid + glossy spheres, ALL-CAPS white headline, white-bezel phone | friendly consumer, lifestyle |
| `fintech` | vivid flat colour, LEFT semibold 2-liner, underlined keyword, dot grid | fintech, SaaS, productivity |
| `glass-ai` | pale blue mesh, LEFT navy headline, frameless glowing screen, pop-outs | AI assistants, chat, SaaS |

Pick by brand personality, not category alone. Show the user 2 themes rendered on their own
frame 1-2 (`--only 1`) and let them choose before rendering everything.

## 2. Config reference (compose.py v2)

Global keys (any of them can also be set per frame to override):

```jsonc
{
  "out_dir": "final", "sizes": ["1320x2868"],
  "theme": "aurora",
  "bg": "#1C8A5F", "bg2": "#06140F",            // brand colours
  "text": "#FFFFFF", "accent": "#5EE6A8", "accent2": "#C9FFE6",
  "locale": "tr",                                // tr/az: correct İ/I in caps & keyword matching
  "background": "aurora",                        // solid|linear|diagonal|aurora|pastel or a dict (below)
  "grain": 0.2,                                  // 0..1 film grain on the background only
  "fonts": {"heavy": "/path/Font-Black.otf"},    // roles: heavy bold semibold medium light serif rounded emoji
  "headline_style": {"font": "heavy", "light_font": "light", "size": 0.088, "leading": 1.1,
                     "caps": false, "highlight": "color", "line2": "accent", "max_lines": 3,
                     "top": 0.055, "width": 0.86},
  "sub_style": {"font": "medium", "scale": 0.40, "opacity": 0.78},
  "device": {"style": "frameless", "width": 0.80, "fit": "bleed", "tilt": 0, "x": 0, "y": null,
             "shadow": true, "glow": true, "glow_color": null, "gap": 0.032, "sync": true},
  "panorama": false, "panorama_decor": [],
  "frames": [ ... ]
}
```

Frame keys:

```jsonc
{
  "screenshot": "raw/01.png",
  "headline": "Hum it.\nWe'll finish it.",   // \n = forced line break (enables line2 styling)
  "highlight": "finish",                       // words styled by headline_style.highlight
  "sub": "Any melody becomes a song",
  "eyebrow": "AI assistant",                   // small pill above the headline (category label)
  "logo": "icon.png", "logo_text": "Pocket",    // hero frame: app icon and/or tracked wordmark
  "rating": {"value": "4.8", "label": "12K ratings"},   // laurel + stars. REAL numbers only
  "chips": ["Voice", "Photo", "Lyrics"],       // feature pills under the headline
  "popouts": [{"crop": [0.03, 0.30, 0.94, 0.12], "scale": 1.15}],
  "decor": [{"emoji": "🐄", "at": [0.88, 0.36], "size": 0.13, "rotate": -12, "layer": "front"}],
  "device": {"tilt": -5},                      // per-frame device override
  "bg": "#..."                                 // per-frame colour shift (Kling-style)
}
```

### v3 keys (layout, devices, texture)

```jsonc
{
  "headline_style": {"align": "left"},            // center (default) | left | right; applies to logo, eyebrow, sub, chips
  "text_pos": "bottom",                            // caption under the phone; phone hangs from the top edge (alias layout:"bottom")
  "headline_style": {"bottom": 0.06},              // bottom margin for text_pos bottom
  "device": {"color": "#FFFFFF", "rim": "#E6E6EA", "bezel": 0.045},   // white bezel (BRIX/orange kits)
  "device": {"color": "#1E3A8A", "rim": "#3B82F6", "bezel": 0.014},   // thin tinted outline (colour-system kit)
  "devices": [                                     // extra phones in this frame (fan, duo, before/after)
    {"screenshot": "raw/03.png", "at": [0.36, 0.1], "width": 0.62, "tilt": 16, "layer": "back"}],
  "pattern": {"type": "dots", "opacity": 0.1, "spacing": 0.045},     // dots|grid|stripes|band|contours|rings
  "panorama_devices": [                            // with panorama:true, phones crossing seams (x in frame units)
    {"screenshot": "raw/01.png", "at": [1.0, 0.1], "width": 0.85, "tilt": 62}],
  "eyebrow_icon": "check", "eyebrow_solid": true,  // "✓ Easy to use" tag (Farhan Shakir kit)
  "rating": {"value": "#1", "label": "in Finance", "stars": false}     // laurel without stars; REAL only
}
```
- `pattern.band`: `{"type": "band", "color": "#8C8778", "opacity": 0.35, "angle": -20, "y": 0.55, "width": 0.7}`
  draws one diagonal band. In panorama mode it runs through every frame.
- `pattern.contours`: topographic lines around `at` (Aweb). `rings`: concentric circles. `stripes`: `angle`, `thick`.
- Text-only hero: `"device": {"style": "none"}` (and no screenshot). These frames are left out of the phone-top sync.

### Headline styles
- `line2: "accent"`: lines after the first are drawn in the accent colour (Melodize, Kling).
- `line2: "light"`: lines after the first use the light weight (MyTunes).
- `highlight`:
  - `color`: keyword in accent.
  - `pill`: accent rounded box behind the keyword (AI Music frame 2). Text colour is automatic or `pill_text`.
  - `gradient`: keyword filled accent→accent2 (AI Music frame 1/3).
  - `underline`: marker stroke behind the keyword.
  - `marker`: solid highlighter block behind the keyword (ASO.dev). Text colour = `marker_text` or the text colour.
  - `none`.
- `caps: true` + `locale: "tr"` gives correct Turkish capitals ("işlerini" → "İŞLERİNİ").
- `font: "serif"` is editorial (Suno) and uses New York, falling back to Georgia. `font: "rounded"` is friendly and uses SF Pro Rounded.

### Background dict (full control)
```jsonc
{"type": "linear", "stops": ["#FF8A3D", ["#E8336B", 0.7], "#8A1FD1"], "angle": 160}
{"type": "mesh", "base": "#06140F", "blobs": [
   {"color": "#1C8A5F", "at": [0.2, -0.04], "r": 0.62, "alpha": 0.9},   // at: [x in frame widths, y in heights]
   {"color": "#5EE6A8", "at": [1.0, 0.27], "r": 0.34, "alpha": 0.38}]}  // r: radius in frame widths
```
Preset backgrounds mirror the light on odd frames automatically, so neighbours differ.

### Device styles
- `frame`: black iPhone with rim, side buttons and Dynamic Island.
- `frameless`: the bare screen with rounded corners and a hairline (Kling, Melodize). Most modern look.
- `glass`: a translucent ring around the screen plus the island (Suno).
- `none`: no device. Use it for a text/hero-only frame.
- `tilt` (degrees, positive = counter-clockwise) rotates the phone. Pop-outs follow the tilt (MyTunes). Use it on 1 frame per set at most, about 4-7°.
- `fit: "full"` keeps the whole phone visible. `bleed` (the default) runs it off the bottom.

### Pop-outs (the single most effective modern trick)
`crop` is a region of the raw screenshot, given as fractions `[x, y, w, h]` or as pixels. It is redrawn at
`scale` (1.1-1.3) with a shadow and a hairline border.
- Without `at`, it sits exactly over its own spot in the phone, so the card looks "lifted" out.
- Use `dx`/`dy` to nudge it, or `at: [x, y]` (canvas fractions) to place it anywhere.
- Crop whole cards or rows on their natural edges. Never cut through text or a chart.
- To find the region, open the raw screenshot, read the pixel bounds, and divide by 1206×2622 or the actual size.

### Decor
- `emoji` uses Apple Color Emoji. `image` is a path, e.g. a transparent PNG. `shape` is `sparkle`, `circle` or `ring`.
- Keys: `at` (centre, canvas fractions), `size` (fraction of W), `rotate`, `opacity`, `blur` (fraction of W), `layer` (`back` = behind the phone, `front` = over it).
- v3 decor kinds:
  - `{"text": "01", "size": 0.95, "color": "#9CCFFF", "outline": false, "stroke": 0.004}` draws a giant numeral or word. `size` = font px / W.
  - `{"badge": "40%\nOFF", "shape": "starburst"|"circle"|"pill"|"tag", "color", "text_color", "rotate", "font_scale"}` draws a sticker. `tag` adds a check icon.
  - shapes `hexagon` (outline), `blob` (organic fill, `seed`; use size > 1 in `panorama_decor`), `sphere` (glossy 3D ball), `wave` (squiggle), `chevrons`.
- 1-3 items per frame. They should echo the app (a note for music, a cow for a farm app), never clutter.
- Never put decor over the important UI.

### Panorama
`"panorama": true` renders one wide background across all frames. `panorama_decor` uses x in **frame
units** (x = 1.0 sits on the seam between frames 1 and 2). A big `ring` or blurred `circle` that crosses
a seam makes the gallery read as one continuous strip when users swipe.

## 3. Narrative per frame (what goes where)

1. **Hero**: logo or wordmark, the core promise in two lines, an optional real rating, and the best screen.
2. **Magic moment**: the differentiator, with a pop-out of the key UI element.
3. **Core loop**: the screen used daily. Chips listing the sub-features.
4. **Trust / depth**: data, history, team, sync. Optional tilt or decor for rhythm.
5+. Supporting features. Keep the system and vary the light.

## 4. Figma recipes (same patterns, editable)

Use Montserrat / Inter / Poppins for text (SF Pro will not render server-side via MCP); for serif use
Playfair Display or DM Serif Display.

- **Aurora/mesh bg**: the frame fill is the dark base. Add 3-4 ellipses (1000-1600px) in brand/accent colours at 40-90% opacity, each with a **Layer blur 300-500**. Mirror them on alternating frames. Grain: a top rectangle with a noise image fill at 6-10% opacity, blend Overlay.
- **Two-tone headline**: one text node with two lines. Apply a ranged fill (accent) to line 2, or a ranged fontName (Light) for the MyTunes style.
- **Gradient keyword**: a ranged fill with a GRADIENT_LINEAR paint on the keyword characters.
- **Pill keyword**: an auto-layout frame (padding 12/28, radius 24, accent fill) containing a text node, placed inline as a separate line; or a rectangle behind the word.
- **Frameless screen**: a rectangle with an image fill, radius 12.5% of width, a 3px stroke white @27%, and a drop shadow (y 40, blur 120, black 45%).
- **Glass device**: the screen rectangle inside a parent rectangle 3.4% larger, fill white @20%, stroke white @47%, radius = screen radius + padding, plus a background blur of 20.
- **Glow**: an ellipse behind the device, accent @50%, layer blur 250.
- **Pop-out**: duplicate the screen rectangle and use a mask or crop to the card region (image fill **CROP** mode). Scale it 115%, add radius 40, a white @55% stroke, and a drop shadow. Place it over the source spot, wider than the phone.
- **Tilt**: rotate the device instance -5°, then group the pop-out with it so they rotate together.
- **Rating laurel**: rating text (Bold 110) + 5 star vectors (#FFC83D) + label; for the laurel use a community laurel SVG or draw leaves as rotated ellipses along an arc.
- **Panorama**: put all frames inside one auto-layout row with 0 gap, then place a big ring or ellipse *outside* the frames, overlapping a seam; turn "clip content" on each frame so each export keeps its half.
- **Eyebrow / chips**: auto-layout pills, radius 999, fill accent @16%, stroke accent @55%, SemiBold 30, tracking +8%.
