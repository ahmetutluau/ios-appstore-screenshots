#!/usr/bin/env python3
"""App Store screenshot composer v3 (Pillow only, no API keys).

Usage:
  python3 compose.py config.json            # every frame + showcase.png
  python3 compose.py config.json --only 3   # a single frame (1-based)
  python3 compose.py --themes               # list theme presets

Minimal config (v1 configs keep working; everything else is optional):
{
  "out_dir": "final", "sizes": ["1320x2868"],
  "theme": "aurora",            # classic aurora sunset duotone light-pop | bold-flat marker mono soft-3d fintech glass-ai
  "bg": "#145C43", "bg2": "#0B241C", "text": "#FFFFFF", "accent": "#5EE6A8", "accent2": "#B8FFE0",
  "locale": "tr",               # tr = Turkish-aware caps (i -> İ)
  "frames": [{"screenshot": "raw/01.png", "headline": "Save smarter,\\nspend happier", "highlight": "smarter,"}]
}
Full reference: references/design-patterns.md (config keys, every pattern, examples).
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

# ------------------------------------------------------------------ fonts
SFD = "/Library/Fonts/SF-Pro-Display-%s.otf"
INTER = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
DEJ = "/usr/share/fonts/truetype/dejavu/DejaVu%s.ttf"
SUPP = "/System/Library/Fonts/Supplemental/%s.ttf"
FONT_ROLES = {
    "heavy": [SFD % "Black", SFD % "Heavy", INTER % "Black", SUPP % "Arial Black", DEJ % "Sans-Bold"],
    "bold": [SFD % "Bold", INTER % "Bold", SUPP % "Arial Bold", DEJ % "Sans-Bold"],
    "semibold": [SFD % "Semibold", INTER % "SemiBold", SUPP % "Arial Bold", DEJ % "Sans-Bold"],
    "medium": [SFD % "Medium", INTER % "Medium", SUPP % "Arial", DEJ % "Sans"],
    "light": [SFD % "Light", SFD % "Regular", INTER % "Light", SUPP % "Arial", DEJ % "Sans"],
    "serif": ["/System/Library/Fonts/NewYork.ttf", SUPP % "Georgia", DEJ % "Serif"],
    "serif-bold": [SUPP % "Georgia Bold", DEJ % "Serif-Bold"],
    "rounded": ["/Library/Fonts/SF-Pro-Rounded-Heavy.otf", "/Library/Fonts/SF-Pro-Rounded-Black.otf"],
    "emoji": ["/System/Library/Fonts/Apple Color Emoji.ttc", "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"],
}
FC_PATTERN = {"heavy": "Inter:black", "bold": "Inter:bold", "semibold": "Inter:semibold",
              "medium": "Inter:medium", "light": "Inter:light", "serif": "serif",
              "serif-bold": "serif:bold", "rounded": "Inter:black", "emoji": "emoji"}
_font_paths, _fonts = {}, {}
FONT_OVERRIDES = {}


def font_path(role):
    if role in _font_paths:
        return _font_paths[role]
    p = FONT_OVERRIDES.get(role)
    if not (p and os.path.exists(p)):
        p = next((c for c in FONT_ROLES.get(role, []) if os.path.exists(c)), None)
    if not p:
        try:
            out = subprocess.run(["fc-match", "-f", "%{file}", FC_PATTERN.get(role, "sans")],
                                 capture_output=True, text=True).stdout
            p = out if out and os.path.exists(out) else None
        except Exception:
            p = None
    if not p and role == "rounded":
        p = font_path("heavy")
    if not p and role != "emoji":
        p = font_path("bold") if role != "bold" else None
    if not p and role not in ("emoji",):
        sys.exit(f"No font for role '{role}'; set \"fonts\": {{\"{role}\": \"/path.ttf\"}} in config.json")
    _font_paths[role] = p
    return p


def font(role, size):
    size = max(8, int(size))
    key = (role, size)
    if key not in _fonts:
        f = ImageFont.truetype(font_path(role), size)
        if role == "serif":
            try:
                f.set_variation_by_name("Medium")
            except Exception:
                pass
        _fonts[key] = f
    return _fonts[key]


# ------------------------------------------------------------------ colour / text helpers
def rgb(h, a=None):
    if isinstance(h, (tuple, list)):
        c = tuple(h[:3]); al = h[3] if len(h) > 3 else 255
    else:
        h = h.lstrip("#")
        c = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        al = int(h[6:8], 16) if len(h) == 8 else 255
    if a is not None:
        al = int(a * 255)
    return c + (al,)


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lum(h):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)[:3]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def is_tr(loc):
    return str(loc).lower().startswith(("tr", "az"))


def upper(s, loc):
    if is_tr(loc):
        s = s.replace("i", "İ").replace("ı", "I")
    return s.upper()


def norm(s, loc):
    s = s.strip(".,!?:;\"'“”")
    if is_tr(loc):
        s = s.replace("İ", "i").replace("I", "ı")
    return s.lower()


def deep(a, b):
    out = dict(a)
    for k, v in (b or {}).items():
        out[k] = deep(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def comp(base, el, x, y):
    """alpha-composite el onto base at (x, y), clipping at the edges."""
    x, y = int(round(x)), int(round(y))
    l, t = max(0, -x), max(0, -y)
    r, b = min(el.width, base.width - x), min(el.height, base.height - y)
    if r <= l or b <= t:
        return
    base.alpha_composite(el.crop((l, t, r, b)) if (l, t, r, b) != (0, 0, el.width, el.height) else el,
                         (x + l, y + t))


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], int(r), fill=255)
    return m


def soft(mask, blur):
    """fast large Gaussian blur of an L mask (blur at 1/4 res)."""
    if blur <= 0:
        return mask
    f = 4 if blur > 12 else 1
    sm = mask.resize((max(1, mask.width // f), max(1, mask.height // f)), Image.BILINEAR)
    sm = sm.filter(ImageFilter.GaussianBlur(blur / f))
    return sm.resize(mask.size, Image.BICUBIC)


def shadow_of(el, blur, alpha, color="#000000"):
    pad = int(blur * 3)
    m = Image.new("L", (el.width + 2 * pad, el.height + 2 * pad), 0)
    m.paste(el.getchannel("A"), (pad, pad))
    m = soft(m, blur).point(lambda v: int(v * alpha))
    sh = Image.new("RGBA", m.size, rgb(color, 0))
    sh.putalpha(m)
    return sh, pad


def drop_shadow(base, el, x, y, blur, alpha, dy=0, color="#000000"):
    sh, pad = shadow_of(el, blur, alpha, color)
    comp(base, sh, x - pad, y - pad + dy)


# ------------------------------------------------------------------ themes
THEMES = {
    "classic": ("Flat/vertical brand gradient, framed phone, coloured keyword. Safe default.",
                {"background": "linear", "device": {"style": "frame"},
                 "headline_style": {"font": "heavy", "highlight": "color"}}),
    "aurora": ("Dark base + blurred brand-colour light blobs, frameless screen, glow, line 2 in accent. "
               "Premium/AI/tech (Kling, Melodize).",
               {"background": "aurora", "grain": 0.22,
                "device": {"style": "frameless", "glow": True, "width": 0.80},
                "headline_style": {"font": "bold", "line2": "accent", "highlight": "color", "size": 0.084}}),
    "sunset": ("Vivid warm diagonal gradient, editorial serif headline, glass-ring phone. "
               "Lifestyle/creative (Suno).",
               {"background": "diagonal", "grain": 0.18, "device": {"style": "glass", "width": 0.78},
                "headline_style": {"font": "serif", "highlight": "none", "size": 0.088, "leading": 1.04}}),
    "duotone": ("Two-colour diagonal gradient, bold line 1 + light line 2, framed phone, pop-outs. "
                "Utility/productivity (MyTunes).",
                {"background": "diagonal", "device": {"style": "frame", "width": 0.80},
                 "headline_style": {"font": "heavy", "line2": "light", "highlight": "none", "size": 0.082}}),
    "light-pop": ("Light pastel mesh, ALL-CAPS heavy headline with gradient/pill keyword, framed phone, "
                  "decor. Consumer/fun (AI Music).",
                  {"background": "pastel", "device": {"style": "frame", "width": 0.80},
                   "headline_style": {"font": "heavy", "caps": True, "highlight": "gradient", "size": 0.092,
                                      "leading": 1.08}}),
    # ---- v3 families distilled from 17 Figma community kits (references/figma-examples.md)
    "bold-flat": ("Solid saturated colour, LEFT-aligned heavy headline, big framed phone, often tilted / "
                  "bleeding, stickers + people cut-outs. Consumer, edtech, food, fitness (AppLaunchpad, Aweb, BRIX).",
                  {"background": "solid", "device": {"style": "frame", "width": 0.84},
                   "headline_style": {"font": "heavy", "align": "left", "size": 0.094, "leading": 1.02,
                                      "highlight": "color", "width": 0.84}}),
    "marker": ("Light flat bg, black heavy centred headline, highlighter-marker keyword, huge faded number "
               "behind the phone, laurel hero. Playful utilities (ASO.dev creator).",
               {"background": "linear", "text": "#111111", "device": {"style": "frame", "width": 0.80},
                "headline_style": {"font": "heavy", "highlight": "marker", "size": 0.086, "leading": 1.12}}),
    "mono": ("Charcoal gradient, thin light-weight centred title, realistic black phone, numbers / lens "
             "callouts. Premium minimal, dev tools, finance (const lab, Farhan Shakir).",
             {"background": "linear", "bg": "#4A4A4E", "bg2": "#1C1C1E", "text": "#FFFFFF",
              "device": {"style": "frame", "width": 0.80},
              "headline_style": {"font": "light", "highlight": "none", "size": 0.074, "leading": 1.15}}),
    "soft-3d": ("Warm solid colour with glossy 3D spheres, ALL-CAPS white headline, white-bezel phone. "
                "Friendly consumer (Arzu Cetinkaya orange kit).",
                {"background": "solid", "device": {"style": "frame", "width": 0.80, "color": "#FFFFFF",
                                                     "rim": "#ECECEC"},
                 "headline_style": {"font": "heavy", "caps": True, "highlight": "none", "size": 0.080},
                 "decor": [{"shape": "sphere", "at": [0.9, 0.08], "size": 0.22},
                           {"shape": "sphere", "at": [0.06, 0.55], "size": 0.30},
                           {"shape": "sphere", "at": [0.85, 0.82], "size": 0.16}]}),
    "fintech": ("Vivid flat colour per frame, LEFT-aligned 2-line semibold headline with underlined keyword, "
                "dot-grid texture, sparkle icon, phone bottom. Fintech, SaaS, productivity (FREE templates kit).",
                {"background": "solid", "pattern": {"type": "dots", "opacity": 0.10, "spacing": 0.045},
                 "device": {"style": "frame", "width": 0.82},
                 "headline_style": {"font": "bold", "align": "left", "size": 0.078, "leading": 1.1,
                                    "highlight": "underline", "width": 0.84}}),
    "glass-ai": ("Pale blue mesh, LEFT-aligned navy headline, frameless glowing screen, floating UI cards; "
                 "mirror set in deep navy. AI assistants, chat, SaaS (BRIX AI kit).",
                 {"background": "pastel", "text": "#0B1B4D", "grain": 0.06,
                  "device": {"style": "frameless", "width": 0.80, "glow": True},
                  "headline_style": {"font": "bold", "align": "left", "size": 0.082, "highlight": "color",
                                     "width": 0.84}}),
}
DEFAULTS = {
    "theme": "classic", "bg": "#0E7C66", "text": "#FFFFFF", "accent": "#FFD84D", "locale": "en", "grain": 0,
    "device": {"style": "frame", "width": 0.80, "fit": "bleed", "tilt": 0, "x": 0, "y": None,
               "shadow": True, "glow": False, "gap": 0.032, "sync": True,
               "color": "#101012", "rim": "#696972", "bezel": 0.032},
    "text_pos": "top",            # top | bottom (caption under the phone, phone hangs from the top edge)
    "headline_style": {"font": "heavy", "light_font": "light", "size": 0.088, "min_size": 0.05,
                       "max_lines": 3, "leading": None, "caps": False, "highlight": "color",
                       "line2": None, "top": 0.055, "bottom": 0.06, "width": 0.86, "align": "center"},
    "sub_style": {"font": "medium", "scale": 0.40, "opacity": 0.78},
}


def resolve(cfg, frame):
    theme = frame.get("theme") or cfg.get("theme") or "classic"
    if theme not in THEMES:
        sys.exit(f"unknown theme '{theme}'; choose from {', '.join(THEMES)}")
    g = deep(deep(DEFAULTS, THEMES[theme][1]), {k: v for k, v in cfg.items() if k != "frames"})
    c = deep(g, frame)
    if c.get("layout") == "full" and "fit" not in (cfg.get("device") or {}) | (frame.get("device") or {}):
        c["device"] = deep(c["device"], {"fit": "full", "width": 0.74})
    if theme == "light-pop" and "text" not in cfg and "text" not in frame:
        c["text"] = "#15122B"
    if c.get("layout") == "bottom":   # alias
        c["text_pos"] = "bottom"
    return c


def ax(c, W, w):
    """x of a w-wide item for the configured alignment (headline_style.align)."""
    hs = c["headline_style"]
    m = W * (1 - hs["width"]) / 2
    a = hs.get("align", "center")
    return m if a == "left" else (W - m - w if a == "right" else (W - w) / 2)


# ------------------------------------------------------------------ backgrounds
def bg_spec(c, idx=0):
    b = c.get("background", "linear")
    if isinstance(b, dict):
        return b
    bg = c["bg"]
    bg2 = c.get("bg2") or bg
    acc = c["accent"]
    acc2 = c.get("accent2") or mix(acc, "#FFFFFF", 0.35)
    flip = idx % 2 == 1
    X = (lambda x: 1 - x) if flip else (lambda x: x)
    if b == "solid":
        return {"type": "solid", "color": bg}
    if b == "linear":
        return {"type": "linear", "stops": [bg, bg2], "angle": 180}
    if b == "diagonal":
        return {"type": "linear", "stops": [bg, bg2], "angle": 205 if flip else 155}
    if b == "aurora":
        base = c.get("bg2") or mix(bg, "#000000", 0.75)
        return {"type": "mesh", "base": base, "blobs": [
            {"color": bg, "at": [X(0.22), -0.04], "r": 0.62, "alpha": 0.9},
            {"color": acc, "at": [X(1.02), 0.27], "r": 0.34, "alpha": 0.38},
            {"color": acc2, "at": [X(-0.02), 0.58], "r": 0.30, "alpha": 0.16},
            {"color": bg, "at": [X(0.8), 1.06], "r": 0.62, "alpha": 0.75}]}
    if b == "pastel":
        return {"type": "mesh", "base": mix(acc, "#FFFFFF", 0.92), "blobs": [
            {"color": acc, "at": [X(0.05), 0.08], "r": 0.6, "alpha": 0.32},
            {"color": acc2, "at": [X(1.0), 0.45], "r": 0.6, "alpha": 0.30},
            {"color": bg, "at": [X(0.2), 0.98], "r": 0.7, "alpha": 0.22}]}
    sys.exit(f"unknown background '{b}' (solid|linear|diagonal|aurora|pastel or a dict)")


def _interp(stops, t):
    t = min(1.0, max(0.0, t))
    for (c1, p1), (c2, p2) in zip(stops, stops[1:]):
        if t <= p2:
            k = 0 if p2 == p1 else (t - p1) / (p2 - p1)
            return tuple(round(c1[i] + (c2[i] - c1[i]) * k) for i in range(4))
    return stops[-1][0]


def linear_img(W, H, stops, angle, f=12):
    if len(stops) == 1:
        stops = stops * 2
    st = [(rgb(s[0]), s[1]) if isinstance(s, list) else (rgb(s), i / (len(stops) - 1))
          for i, s in enumerate(stops)]
    lw, lh = max(2, W // f), max(2, H // f)
    a = math.radians(angle)
    dx, dy = math.sin(a), -math.cos(a)
    L = (abs(dx) * lw / 2 + abs(dy) * lh / 2) or 1
    px = [_interp(st, ((x - lw / 2) * dx + (y - lh / 2) * dy) / L * 0.5 + 0.5)
          for y in range(lh) for x in range(lw)]
    im = Image.new("RGBA", (lw, lh))
    im.putdata(px)
    return im.resize((W, H), Image.BICUBIC)


def render_bg(W, H, spec, unit):
    t = spec.get("type", "linear")
    if t == "solid":
        return Image.new("RGBA", (W, H), rgb(spec["color"]))
    if t == "linear":
        return linear_img(W, H, spec["stops"], spec.get("angle", 180))
    if t == "mesh":
        f = 8
        lw, lh = W // f + 1, H // f + 1
        u = unit / f
        img = Image.new("RGBA", (lw, lh), rgb(spec["base"]))
        for b in spec.get("blobs", []):
            r = b.get("r", 0.5) * u
            cx, cy = b["at"][0] * u, b["at"][1] * lh
            m = Image.new("L", (lw, lh), 0)
            ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=int(255 * b.get("alpha", 1)))
            m = m.filter(ImageFilter.GaussianBlur(r * 0.6))
            img = Image.composite(Image.new("RGBA", (lw, lh), rgb(b["color"])), img, m)
        return img.resize((W, H), Image.BICUBIC)
    sys.exit(f"unknown background type '{t}'")


def add_grain(img, amt):
    if not amt:
        return img
    n = Image.effect_noise(img.size, 48).convert("RGB")
    base = img.convert("RGB")
    return Image.blend(base, ImageChops.soft_light(base, n), min(1.0, amt)).convert("RGBA")


def add_pattern(img, p, c, unit):
    """texture over the background. p = {"type": dots|grid|stripes|band|contours|rings, ...}
    common keys: color (default text colour), opacity, spacing (fraction of frame width)."""
    if not p:
        return img
    if isinstance(p, str):
        p = {"type": p}
    t = p.get("type", "dots")
    W, H = img.size
    col = p.get("color") or c["text"]
    op = p.get("opacity", 0.12)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    s = max(6, unit * p.get("spacing", 0.045))
    fill = rgb(col, op)
    lw = max(2, int(unit * p.get("line", 0.003)))
    if t == "dots":
        r = max(2, s * p.get("dot", 0.09))
        y = s / 2
        while y < H:
            x = s / 2
            while x < W:
                d.ellipse([x - r, y - r, x + r, y + r], fill=fill)
                x += s
            y += s
    elif t == "grid":
        x = 0
        while x < W:
            d.line([x, 0, x, H], fill=fill, width=lw); x += s
        y = 0
        while y < H:
            d.line([0, y, W, y], fill=fill, width=lw); y += s
    elif t == "stripes":
        a = math.radians(p.get("angle", 45))
        L = W + H
        k = -L
        while k < L:
            d.line([k, 0, k + H * math.tan(a), H], fill=fill, width=int(s * p.get("thick", 0.18)))
            k += s
    elif t == "band":   # one wide diagonal band of a second colour (Farhan Shakir / LT "White" set)
        fill = rgb(p.get("color") or c.get("bg2") or c["accent"], p.get("opacity", 1.0))
        a = math.radians(p.get("angle", -18))
        cy, bw = H * p.get("y", 0.62), unit * p.get("width", 0.55)
        dx = W * 4
        pts = [(-dx, cy - dx * math.tan(a)), (dx, cy + dx * math.tan(a))]
        d.polygon([pts[0], pts[1], (pts[1][0], pts[1][1] + bw), (pts[0][0], pts[0][1] + bw)], fill=fill)
    elif t in ("contours", "rings"):   # topographic lines (Aweb) / concentric rings
        cx, cy = p.get("at", [0.8, 0.75])
        cx, cy = cx * unit, cy * H
        n = p.get("count", 26)
        for i in range(1, n + 1):
            R = s * i * 0.5
            if t == "rings":
                d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=fill, width=lw)
                continue
            pts = []
            for k in range(73):
                th = 2 * math.pi * k / 72
                wob = 1 + 0.16 * math.sin(3 * th + i * 0.35) + 0.07 * math.sin(5 * th - i * 0.2)
                pts.append((cx + R * 1.25 * wob * math.cos(th), cy + R * wob * math.sin(th)))
            d.line(pts, fill=fill, width=lw, joint="curve")
    else:
        sys.exit(f"unknown pattern '{t}' (dots|grid|stripes|band|contours|rings)")
    img = img.copy()
    img.alpha_composite(lay)
    return img


# ------------------------------------------------------------------ device
def build_device(shot, pw, style, dv=None):
    """-> (RGBA device image, (sx, sy, sw) screen origin/width inside it).
    dv (optional) may set color (body), rim (outer edge) and bezel (fraction of width) for style 'frame':
    white bezel = {"color": "#FFFFFF", "rim": "#E6E6EA"}; thin coloured outline = {"color": accent, "bezel": 0.014}."""
    dv = dv or {}
    if style == "frame":
        body = rgb(dv.get("color") or "#101012")
        rim = rgb(dv.get("rim") or "#696972")
        btn = max(4, int(pw * 0.011))
        body_w = pw - 2 * btn
        bezel = max(2, int(body_w * dv.get("bezel", 0.032)))
        sw = body_w - 2 * bezel
        sh = round(shot.height * sw / shot.width)
        bh = sh + 2 * bezel
        im = Image.new("RGBA", (pw, bh), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        bc = rgb(mix(body, rim, 0.45))
        for y0, y1 in ((0.165, 0.195), (0.235, 0.29), (0.31, 0.365)):
            d.rounded_rectangle([0, bh * y0, btn * 2, bh * y1], btn, fill=bc)
        d.rounded_rectangle([pw - btn * 2, bh * 0.25, pw - 1, bh * 0.35], btn, fill=bc)
        ro = int(body_w * 0.135)
        d.rounded_rectangle([btn, 0, btn + body_w - 1, bh - 1], ro, fill=body)
        w = max(3, pw // 260)
        d.rounded_rectangle([btn, 0, btn + body_w - 1, bh - 1], ro, outline=rim, width=w)
        d.rounded_rectangle([btn + w, w, btn + body_w - 1 - w, bh - 1 - w], ro - w,
                            outline=rgb(mix(body, "#000000", 0.25)), width=w)
        sx, sy = btn + bezel, bezel
        im.paste(shot.resize((sw, sh), Image.LANCZOS), (sx, sy), rounded_mask((sw, sh), ro - bezel))
        island = True
    else:
        pad = int(pw * 0.034) if style == "glass" else 0
        sw = pw - 2 * pad
        sh = round(shot.height * sw / shot.width)
        r = int(sw * 0.125)
        im = Image.new("RGBA", (pw, sh + 2 * pad), (0, 0, 0, 0))
        if pad:
            d = ImageDraw.Draw(im)
            d.rounded_rectangle([0, 0, pw - 1, im.height - 1], r + pad, fill=(255, 255, 255, 52))
            d.rounded_rectangle([0, 0, pw - 1, im.height - 1], r + pad, outline=(255, 255, 255, 120),
                                width=max(2, pw // 400))
        sx, sy = pad, pad
        im.paste(shot.resize((sw, sh), Image.LANCZOS), (sx, sy), rounded_mask((sw, sh), r))
        ImageDraw.Draw(im, "RGBA").rounded_rectangle([sx, sy, sx + sw - 1, sy + sh - 1], r,
                                                    outline=(255, 255, 255, 70), width=max(2, pw // 450))
        island = style == "glass"
    if island:
        iw, ih = int(sw * 0.31), int(sw * 0.09)
        ix, iy = sx + (sw - iw) // 2, sy + int(sw * 0.027)
        ImageDraw.Draw(im).rounded_rectangle([ix, iy, ix + iw, iy + ih], ih // 2, fill=(0, 0, 0, 255))
    return im, (sx, sy, sw)


def rot_point(x, y, w, h, nw, nh, deg):
    """map (x, y) in a w*h image to the canvas of img.rotate(deg, expand=True) (nw*nh)."""
    a = math.radians(deg)
    dx, dy = x - w / 2, y - h / 2
    return nw / 2 + dx * math.cos(a) + dy * math.sin(a), nh / 2 - dx * math.sin(a) + dy * math.cos(a)


# ------------------------------------------------------------------ decor
def make_decor(it, W, c, base):
    size = int(W * it.get("size", 0.08))
    col = it.get("color") or c["accent"]
    if "emoji" in it:
        fp = font_path("emoji")
        if not fp:
            return None
        f = ImageFont.truetype(fp, 160 if "Apple" in fp else 109)
        tmp = Image.new("RGBA", (260, 260), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((20, 20), it["emoji"], font=f, embedded_color=True)
        tmp = tmp.crop(tmp.getbbox() or (0, 0, 1, 1))
        el = tmp.resize((size, max(1, int(tmp.height * size / tmp.width))), Image.LANCZOS)
    elif "image" in it:
        im = Image.open(os.path.join(base, it["image"])).convert("RGBA")
        el = im.resize((size, max(1, int(im.height * size / im.width))), Image.LANCZOS)
    elif "text" in it:   # giant number / word behind the phone (ASO.dev "1", const lab "2")
        f = font(it.get("font", "heavy"), size)
        s = upper(it["text"], c["locale"]) if it.get("caps") else it["text"]
        tmp = Image.new("RGBA", (int(f.getlength(s) + size), int(size * 1.6)), (0, 0, 0, 0))
        dd = ImageDraw.Draw(tmp)
        sw_ = int(W * it.get("stroke", 0))
        if it.get("outline"):
            dd.text((size * 0.5, size * 0.2), s, font=f, fill=(0, 0, 0, 0), stroke_width=max(2, sw_ or W // 160),
                    stroke_fill=rgb(col))
        else:
            dd.text((size * 0.5, size * 0.2), s, font=f, fill=rgb(col), stroke_width=sw_,
                    stroke_fill=rgb(it.get("stroke_color", col)))
        el = tmp.crop(tmp.getbbox() or (0, 0, 1, 1))
    elif "badge" in it:  # sticker: pill | starburst | circle | tag (with check)
        shape = it.get("shape", "pill")
        tc = rgb(it.get("text_color") or ("#111111" if lum(col) > 0.45 else "#FFFFFF"))
        lines = it["badge"].split("\n")
        fs = int(size * it.get("font_scale", 0.18 if shape in ("starburst", "circle") else 0.16))
        f = font(it.get("font", "heavy"), fs)
        tw = max(f.getlength(ln) for ln in lines)
        th = fs * 1.15 * len(lines)
        if shape in ("starburst", "circle"):
            el = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            dd = ImageDraw.Draw(el)
            R = size / 2
            if shape == "circle":
                dd.ellipse([0, 0, size - 1, size - 1], fill=rgb(col))
            else:
                n = it.get("points", 16)
                dd.polygon([(R + (R if k % 2 == 0 else R * 0.82) * math.cos(math.pi * k / n),
                             R + (R if k % 2 == 0 else R * 0.82) * math.sin(math.pi * k / n)) for k in range(2 * n)],
                           fill=rgb(col))
        else:
            px_, py_ = fs * 0.9, fs * 0.55
            icon = fs * 1.1 if shape == "tag" else 0
            el = Image.new("RGBA", (int(tw + 2 * px_ + icon), int(th + 2 * py_)), (0, 0, 0, 0))
            dd = ImageDraw.Draw(el)
            dd.rounded_rectangle([0, 0, el.width - 1, el.height - 1],
                                 el.height / 2 if shape == "pill" else fs * 0.3, fill=rgb(col))
            if icon:
                cx_, cy_, r_ = px_ + fs * 0.4, el.height / 2, fs * 0.42
                dd.ellipse([cx_ - r_, cy_ - r_, cx_ + r_, cy_ + r_], fill=tc)
                dd.line([(cx_ - r_ * 0.45, cy_), (cx_ - r_ * 0.1, cy_ + r_ * 0.35), (cx_ + r_ * 0.5, cy_ - r_ * 0.35)],
                        fill=rgb(col), width=max(2, int(fs * 0.12)))
        y_ = (el.height - th) / 2 + fs * 0.9
        for ln in lines:
            x_ = (el.width - f.getlength(ln)) / 2 + (fs * 0.55 if shape == "tag" else 0)
            dd.text((x_, y_), ln, font=f, fill=tc, anchor="ls")
            y_ += fs * 1.15
    else:
        shape = it.get("shape", "circle")
        el = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(el)
        R = size / 2
        if shape == "sparkle":
            pts = []
            for k in range(8):
                rr = R if k % 2 == 0 else R * 0.2
                a = math.pi / 4 * k - math.pi / 2
                pts.append((R + rr * math.cos(a), R + rr * math.sin(a)))
            d.polygon(pts, fill=rgb(col))
        elif shape == "ring":
            d.ellipse([2, 2, size - 3, size - 3], outline=rgb(col), width=max(2, int(size * 0.06)))
        elif shape == "hexagon":   # outline hexagon (Lauren Tobolski kit)
            pts = [(R + (R - 4) * math.cos(math.pi / 3 * k + math.pi / 6),
                    R + (R - 4) * math.sin(math.pi / 3 * k + math.pi / 6)) for k in range(6)]
            d.polygon(pts, outline=rgb(col), width=max(3, int(size * it.get("weight", 0.07))))
        elif shape == "blob":      # organic filled shape; big ones crossing seams = 500+ kit panoramas
            seed = it.get("seed", 3)
            pts = []
            for k in range(90):
                th = 2 * math.pi * k / 90
                rr = R * (0.82 + 0.1 * math.sin(2 * th + seed) + 0.07 * math.sin(3 * th + seed * 1.7))
                pts.append((R + rr * math.cos(th), R + rr * math.sin(th)))
            d.polygon(pts, fill=rgb(col))
        elif shape == "sphere":    # glossy 3D ball (orange kit)
            base_c = it.get("color") or mix(c["bg"], "#FFFFFF", 0.25)
            ball = Image.new("RGBA", (size, size), rgb(mix(base_c, "#000000", 0.18)))
            hl = Image.new("L", (size, size), 0)
            ImageDraw.Draw(hl).ellipse([size * 0.12, size * 0.06, size * 0.7, size * 0.62], fill=255)
            hl = hl.filter(ImageFilter.GaussianBlur(size * 0.14))
            ball = Image.composite(Image.new("RGBA", (size, size), rgb(mix(base_c, "#FFFFFF", 0.45))), ball, hl)
            el = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            el.paste(ball, (0, 0), rounded_mask((size, size), size / 2))
        elif shape == "wave":      # squiggle line
            amp, n = size * 0.12, it.get("waves", 3)
            pts = [(x, R + amp * math.sin(x / size * n * 2 * math.pi)) for x in range(0, size, 3)]
            d.line(pts, fill=rgb(col), width=max(3, int(size * it.get("weight", 0.04))), joint="curve")
        elif shape == "chevrons":  # >>> marks
            wgt = max(3, int(size * 0.07))
            for k in range(3):
                x0 = size * (0.1 + k * 0.28)
                d.line([(x0, size * 0.3), (x0 + size * 0.18, R), (x0, size * 0.7)], fill=rgb(col), width=wgt)
        else:
            d.ellipse([0, 0, size - 1, size - 1], fill=rgb(col))
    if it.get("opacity", 1) < 1:
        op = it["opacity"]
        el.putalpha(el.getchannel("A").point(lambda v: int(v * op)))
    if it.get("rotate"):
        el = el.rotate(it["rotate"], Image.BICUBIC, expand=True)
    if it.get("blur"):
        b = int(it["blur"] * W)
        pad = b * 3
        big = Image.new("RGBA", (el.width + 2 * pad, el.height + 2 * pad), (0, 0, 0, 0))
        big.paste(el, (pad, pad))
        el = big.filter(ImageFilter.GaussianBlur(b))
    return el


def draw_decor(img, items, c, unit, H, layer):
    for it in items or []:
        if it.get("layer", "back") != layer:
            continue
        el = make_decor(it, unit, c, c["_base"])
        if el is not None:
            comp(img, el, it["at"][0] * unit - el.width / 2, it["at"][1] * H - el.height / 2)


# ------------------------------------------------------------------ text block
def text_width(d, s, f):
    return d.textlength(s, font=f)


def tracked(d, xy, s, f, fill, track):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill, anchor="ls")
        x += d.textlength(ch, font=f) + track


def tracked_width(d, s, f, track):
    return sum(d.textlength(ch, font=f) for ch in s) + track * max(0, len(s) - 1)


def draw_logo(txt, d, c, W, y):
    if c.get("logo"):
        s = int(W * c.get("logo_size", 0.16))
        im = Image.open(os.path.join(c["_base"], c["logo"])).convert("RGBA").resize((s, s), Image.LANCZOS)
        m = rounded_mask((s, s), s * 0.225)
        im.putalpha(ImageChops.multiply(im.getchannel("A"), m))
        drop_shadow(txt, im, ax(c, W, s), y, W * 0.02, 0.35, dy=W * 0.01)
        comp(txt, im, ax(c, W, s), y)
        y += s + W * 0.035
    if c.get("logo_text"):
        f = font(c.get("logo_font", "heavy"), W * 0.062)
        s = upper(c["logo_text"], c["locale"]) if c.get("logo_caps", True) else c["logo_text"]
        tr = f.size * 0.12
        tw = tracked_width(d, s, f, tr)
        asc = f.getmetrics()[0]
        tracked(d, (ax(c, W, tw), y + asc), s, f, rgb(c["text"]), tr)
        y += f.size * 1.35
    return y + W * 0.01


def draw_eyebrow(txt, d, c, W, y):
    f = font("bold", W * 0.027)
    s = upper(c["eyebrow"], c["locale"])
    tr = f.size * 0.08
    tw = tracked_width(d, s, f, tr)
    px, h = W * 0.032, f.size * 2.15
    col = c.get("eyebrow_color") or c["accent"]
    icon = f.size * 1.25 if c.get("eyebrow_icon") == "check" else 0
    x0 = ax(c, W, tw + 2 * px + icon)
    solid = c.get("eyebrow_solid")
    d.rounded_rectangle([x0, y, x0 + tw + 2 * px + icon, y + h], h / 2 if not solid else h * 0.22,
                        fill=rgb(col, 1.0 if solid else 0.16), outline=rgb(col, 0.55), width=max(2, W // 600))
    asc, desc = f.getmetrics()
    tcol = (rgb("#111111") if lum(col) > 0.45 else rgb("#FFFFFF")) if solid else rgb(col)
    if icon:  # check-mark tag (Farhan Shakir "Easy to use")
        cx, cy, r = x0 + px + f.size * 0.45, y + h / 2, f.size * 0.5
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tcol)
        d.line([(cx - r * 0.45, cy), (cx - r * 0.1, cy + r * 0.35), (cx + r * 0.5, cy - r * 0.35)],
               fill=rgb(col) if solid else rgb(c["bg"]), width=max(2, int(f.size * 0.13)))
    tracked(d, (x0 + px + icon, y + h / 2 + (asc - desc) / 2 - f.size * 0.04), s, f, tcol, tr)
    return y + h + W * 0.034


def draw_headline(txt, d, c, W, y):
    hs, loc = c["headline_style"], c["locale"]
    hl = {norm(w, loc) for w in (c.get("highlight") or "").split()}
    words = []
    for li, line in enumerate(c["headline"].split("\n")):
        for w in line.split():
            words.append((upper(w, loc) if hs["caps"] else w, norm(w, loc) in hl, li))
    style = hs["highlight"]
    max_w = W * hs["width"]
    size = W * hs["size"]

    def fonts_for(sz):
        main = font(hs["font"], sz)
        second = font(hs["light_font"], sz) if hs.get("line2") == "light" else main
        return main, second

    def wrap(sz):
        main, second = fonts_for(sz)
        pad = sz * 0.17 if style == "pill" else 0
        lines, cur, cur_w, cur_li = [], [], 0, None
        for wd in words:
            f = main if wd[2] == 0 else second
            ww = text_width(d, wd[0], f) + (2 * pad if wd[1] else 0)
            sp = text_width(d, " ", f)
            if cur and (wd[2] != cur_li or cur_w + sp + ww > max_w):
                lines.append((cur, cur_w)); cur, cur_w = [], 0
            cur_w += (sp if cur else 0) + ww
            cur.append(wd); cur_li = wd[2]
        if cur:
            lines.append((cur, cur_w))
        return lines

    while True:
        lines = wrap(size)
        if (len(lines) <= hs["max_lines"] and all(w <= max_w for _, w in lines)) or size <= W * hs["min_size"]:
            break
        size -= W * 0.003
    main, second = fonts_for(size)
    lead = hs.get("leading") or (1.2 if style == "pill" else 1.1)
    text_c, acc = c["text"], c["accent"]
    acc2 = c.get("accent2") or mix(acc, "#FFFFFF", 0.35)
    pill_text = c.get("pill_text") or ("#111111" if lum(acc) > 0.45 else "#FFFFFF")
    pad = size * 0.17
    yb = y + main.getmetrics()[0] + (pad * 0.5 if style == "pill" else 0)
    for words_in, lw in lines:
        x = ax(c, W, lw)
        spans, i = [], 0
        while i < len(words_in):  # group runs of highlighted words into one span
            j = i + 1
            if words_in[i][1] and style in ("pill", "gradient", "underline", "marker"):
                while j < len(words_in) and words_in[j][1]:
                    j += 1
            spans.append(words_in[i:j]); i = j
        for k, sp in enumerate(spans):
            s = " ".join(w[0] for w in sp)
            is_hl, li = sp[0][1], sp[0][2]
            f = main if li == 0 else second
            col = acc if (li > 0 and hs.get("line2") == "accent") else text_c
            l, t, r, b = f.getbbox(s, anchor="ls")
            if is_hl and style == "pill":
                x += pad
                d.rounded_rectangle([x + l - pad, yb + t - pad * 0.62, x + r + pad, yb + size * 0.1 + pad * 0.62],
                                    size * 0.2, fill=rgb(acc))
                d.text((x, yb), s, font=f, fill=rgb(pill_text), anchor="ls")
                x += pad
            elif is_hl and style == "gradient":
                m = Image.new("L", (int(r - l) + 4, int(b - t) + 4), 0)
                ImageDraw.Draw(m).text((-l + 2, -t + 2), s, font=f, fill=255, anchor="ls")
                g = linear_img(m.width, m.height, [acc, acc2], 90, f=4)
                txt.paste(g, (int(x + l - 2), int(yb + t - 2)), m)
            elif is_hl and style == "marker":   # highlighter block behind the word (ASO.dev)
                d.rounded_rectangle([x + l - size * 0.07, yb + t - size * 0.06, x + r + size * 0.07,
                                     yb + size * 0.14], size * 0.05, fill=rgb(acc))
                d.text((x, yb), s, font=f, fill=rgb(c.get("marker_text") or col), anchor="ls")
            elif is_hl and style == "underline":
                d.rounded_rectangle([x + l - size * 0.04, yb - size * 0.26, x + r + size * 0.04, yb + size * 0.07],
                                    size * 0.06, fill=rgb(acc, 0.55))
                d.text((x, yb), s, font=f, fill=rgb(col), anchor="ls")
            else:
                use = acc if (is_hl and style == "color") else col
                d.text((x, yb), s, font=f, fill=rgb(use), anchor="ls")
            x += text_width(d, s, f) + (text_width(d, " ", f) if k < len(spans) - 1 else 0)
        yb += size * lead
    return yb - size * lead + main.getmetrics()[1] + (pad * 0.6 if style == "pill" else 0), size


def draw_sub(txt, d, c, W, y, hsize):
    ss = c["sub_style"]
    f = font(ss["font"], max(W * 0.032, hsize * ss["scale"]))
    words, lines, cur = c["sub"].split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if cur and text_width(d, t, f) > W * min(0.8, c["headline_style"]["width"]):
            lines.append(cur); cur = w
        else:
            cur = t
    lines.append(cur)
    y += f.size * 0.55
    asc, desc = f.getmetrics()
    for ln in lines:
        d.text((ax(c, W, text_width(d, ln, f)), y + asc), ln, font=f, fill=rgb(c["text"], ss["opacity"]),
               anchor="ls")
        y += f.size * 1.3
    return y


def star_pts(cx, cy, R):
    pts = []
    for k in range(10):
        rr = R if k % 2 == 0 else R * 0.45
        a = math.pi / 5 * k - math.pi / 2
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def draw_rating(txt, d, c, W, y):
    rt = c["rating"]
    gold = rgb(rt.get("color", "#FFC83D"))
    tc = rgb(c["text"])
    y += W * 0.03
    fv = font("heavy", W * 0.085)
    fl = font("semibold", W * 0.028)
    asc = fv.getmetrics()[0]
    v = str(rt.get("value", ""))
    d.text(((W - text_width(d, v, fv)) / 2, y + asc), v, font=fv, fill=tc, anchor="ls")
    st, gap = W * 0.022, W * 0.012
    ys = y + asc + W * 0.04
    total = 5 * 2 * st + 4 * gap
    if rt.get("stars", True):   # stars: false -> plain laurel badge ("#1 in Music", "Editors' Choice" - real only)
        for k in range(5):
            d.polygon(star_pts((W - total) / 2 + st + k * (2 * st + gap), ys, st), fill=gold)
        yl = ys + st + W * 0.03
    else:
        total, yl = 0, y + asc + W * 0.03
    lab = rt.get("label", "")
    d.text(((W - text_width(d, lab, fl)) / 2, yl + fl.getmetrics()[0]), lab, font=fl, fill=rgb(c["text"], 0.8),
           anchor="ls")
    bottom = yl + fl.size * 1.2
    cw = max(text_width(d, v, fv), total, text_width(d, lab, fl))
    R = cw / 2 + W * 0.085
    cy = (y + bottom) / 2 + W * 0.01
    leaf_col = rgb(rt.get("laurel_color", c["text"]), 0.9)
    lw_, lh_ = int(W * 0.024), int(W * 0.05)
    leaf = Image.new("RGBA", (lw_, lh_), (0, 0, 0, 0))
    lens = [(lw_ / 2 + side * (lw_ / 2 - 1) * math.sin(math.pi * t / 20), (lh_ - 1) * t / 20)
            for side in (1, -1) for t in (range(21) if side == 1 else range(20, -1, -1))]
    ImageDraw.Draw(leaf).polygon(lens, fill=leaf_col)  # pointed leaf
    Ry = (bottom - y) / 2 + W * 0.03
    for side in (-1, 1):
        for k in range(9):
            phi = math.radians(28 + k * 16)
            px = W / 2 + side * R * math.sin(phi)
            py = cy + Ry * math.cos(phi)
            tx, ty = side * R * math.cos(phi), -Ry * math.sin(phi)
            ang = math.degrees(math.atan2(-ty, tx)) - 90 + side * -38
            sc = 1 - 0.4 * k / 8
            el = leaf.resize((max(2, int(lw_ * sc)), max(2, int(lh_ * sc))), Image.LANCZOS)
            el = el.rotate(ang, Image.BICUBIC, expand=True)
            comp(txt, el, px - el.width / 2, py - el.height / 2)
    return bottom + W * 0.02


def draw_chips(txt, d, c, W, y):
    f = font("semibold", W * 0.029)
    px, h, gap = W * 0.03, f.size * 2.1, W * 0.018
    items = [(s, text_width(d, s, f) + 2 * px) for s in c["chips"]]
    rows, cur, cw = [], [], 0
    for it in items:
        if cur and cw + gap + it[1] > W * 0.9:
            rows.append((cur, cw)); cur, cw = [], 0
        cw += (gap if cur else 0) + it[1]; cur.append(it)
    if cur:
        rows.append((cur, cw))
    y += W * 0.03
    asc, desc = f.getmetrics()
    tc = c["text"]
    for row, rw in rows:
        x = ax(c, W, rw)
        for s, w in row:
            d.rounded_rectangle([x, y, x + w, y + h], h / 2, fill=rgb(tc, 0.12), outline=rgb(tc, 0.3),
                                width=max(2, W // 600))
            d.text((x + px, y + h / 2 + (asc - desc) / 2), s, font=f, fill=rgb(tc), anchor="ls")
            x += w + gap
        y += h + gap
    return y


def text_block(txt, c, W, H, y0=None):
    d = ImageDraw.Draw(txt, "RGBA")
    y = H * c["headline_style"]["top"] if y0 is None else y0
    hsize = W * c["headline_style"]["size"]
    if c.get("logo") or c.get("logo_text"):
        y = draw_logo(txt, d, c, W, y)
    if c.get("eyebrow"):
        y = draw_eyebrow(txt, d, c, W, y)
    if c.get("headline"):
        y, hsize = draw_headline(txt, d, c, W, y)
    if c.get("sub"):
        y = draw_sub(txt, d, c, W, y, hsize)
    if c.get("rating"):
        y = draw_rating(txt, d, c, W, y)
    if c.get("chips"):
        y = draw_chips(txt, d, c, W, y)
    return y


# ------------------------------------------------------------------ frame
def extra_device(img, spec, c, W, H, x_unit=None):
    """secondary phone: spec = {screenshot, at: [cx (frame widths), top (frame heights)], width, tilt,
    style, color, rim, bezel, shadow}. Used for fans, duos and panorama phones that cross seams."""
    dv = deep(c["device"], {k: v for k, v in spec.items() if k in ("style", "color", "rim", "bezel")})
    shot = Image.open(os.path.join(c["_base"], spec["screenshot"])).convert("RGB")
    pw = int(W * spec.get("width", 0.6))
    dev, _ = build_device(shot, pw, dv["style"] if dv["style"] != "none" else "frame", dv)
    tilt = spec.get("tilt", 0)
    rdev = dev.rotate(tilt, Image.BICUBIC, expand=True) if tilt else dev
    cx = spec["at"][0] * (x_unit or W)
    py = spec["at"][1] * H - (rdev.height - dev.height) / 2
    if spec.get("shadow", True):
        drop_shadow(img, rdev, cx - rdev.width / 2, py, W * 0.03, 0.45, dy=W * 0.02)
    comp(img, rdev, cx - rdev.width / 2, py)


def render(c, idx, W, H, base_img=None):
    if base_img is not None:
        img = base_img.copy()
    else:
        img = add_grain(render_bg(W, H, bg_spec(c, idx), W), c["grain"])
        img = add_pattern(img, c.get("pattern"), c, W)
    draw_decor(img, c.get("decor"), c, W, H, "back")
    for spec in c.get("devices") or []:
        if spec.get("layer", "back") == "back":
            extra_device(img, spec, c, W, H)
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bottom = c.get("text_pos") == "bottom"
    if bottom:   # caption under the phone; text bottom-anchored, phone hangs from the top edge
        h_own = text_block(Image.new("RGBA", (W, H)), c, W, H, y0=0)
        y_base = H * (1 - c["headline_style"]["bottom"])
        text_block(txt, c, W, H, y0=y_base - h_own)
        y_text = y_base - (c.get("_sync_h") or h_own)
    else:
        y_text = text_block(txt, c, W, H)
    dv = c["device"]
    if dv["style"] != "none" and c.get("screenshot"):
        shot = Image.open(os.path.join(c["_base"], c["screenshot"])).convert("RGB")
        pw = int(W * dv["width"])
        dev, (sx, sy, sw) = build_device(shot, pw, dv["style"], dv)
        if bottom:
            top = H * dv["y"] if dv.get("y") is not None else y_text - H * dv["gap"] - dev.height
        else:
            top = H * dv["y"] if dv.get("y") is not None else (c.get("_sync_top") or y_text) + H * dv["gap"]
        if dv["fit"] == "full" and not bottom and dev.height > H * 0.975 - top:
            pw = int(pw * (H * 0.975 - top) / dev.height)
            dev, (sx, sy, sw) = build_device(shot, pw, dv["style"], dv)
        s = sw / shot.width
        tilt = dv.get("tilt") or 0
        dw, dh = dev.size
        rdev = dev.rotate(tilt, Image.BICUBIC, expand=True) if tilt else dev
        px = (W - rdev.width) / 2 + W * dv["x"]
        py = top - (rdev.height - dh) / 2
        if dv.get("glow"):
            gc = dv.get("glow_color") or c["accent"]
            gw, gh = int(pw * 1.5), int(pw * 1.7)
            m = Image.new("L", (gw // 4, gh // 4), 0)
            ImageDraw.Draw(m).ellipse([gw // 16, gh // 16, gw // 4 - gw // 16, gh // 4 - gh // 16],
                                      fill=int(255 * dv.get("glow_alpha", 0.5)))
            m = m.filter(ImageFilter.GaussianBlur(gw / 28)).resize((gw, gh), Image.BICUBIC)
            gl = Image.new("RGBA", (gw, gh), rgb(gc, 0))
            gl.putalpha(m)
            comp(img, gl, px + rdev.width / 2 - gw / 2, py + dh * 0.28 - gh / 2)
        if dv.get("shadow"):
            drop_shadow(img, rdev, px, py, W * 0.03, 0.5, dy=W * 0.02)
        comp(img, rdev, px, py)

        for p in c.get("popouts") or []:
            x0, y0, w0, h0 = p["crop"]
            if max(p["crop"]) <= 1:
                x0, y0, w0, h0 = x0 * shot.width, y0 * shot.height, w0 * shot.width, h0 * shot.height
            region = shot.crop((int(x0), int(y0), int(x0 + w0), int(y0 + h0)))
            sc = p.get("scale", 1.15)
            cw, ch = int(region.width * s * sc), int(region.height * s * sc)
            card = region.resize((cw, ch), Image.LANCZOS).convert("RGBA")
            r = W * p.get("radius", 0.03)
            card.putalpha(rounded_mask((cw, ch), r))
            if p.get("border", True):
                ImageDraw.Draw(card, "RGBA").rounded_rectangle([0, 0, cw - 1, ch - 1], r,
                                                              outline=rgb(p.get("border_color", "#FFFFFF"), 0.55),
                                                              width=max(2, W // 450))
            if tilt and p.get("tilt", True):
                card = card.rotate(tilt, Image.BICUBIC, expand=True)
            if "at" in p:
                cx, cy = p["at"][0] * W, p["at"][1] * H
            else:
                lx, ly = sx + (x0 + w0 / 2) * s, sy + (y0 + h0 / 2) * s
                if tilt:
                    lx, ly = rot_point(lx, ly, dw, dh, rdev.width, rdev.height, tilt)
                cx, cy = px + lx, py + ly
            cx += W * p.get("dx", 0)
            cy += H * p.get("dy", 0)
            drop_shadow(img, card, cx - card.width / 2, cy - card.height / 2, W * 0.025, 0.45, dy=W * 0.015)
            comp(img, card, cx - card.width / 2, cy - card.height / 2)
    for spec in c.get("devices") or []:
        if spec.get("layer") == "front":
            extra_device(img, spec, c, W, H)
    draw_decor(img, c.get("decor"), c, W, H, "front")
    img.alpha_composite(txt)
    return img.convert("RGB")


# ------------------------------------------------------------------ main
def main():
    if "--themes" in sys.argv:
        for k, (desc, _) in THEMES.items():
            print(f"{k:10s} {desc}")
        return
    cfg_path = sys.argv[1]
    only = int(sys.argv[sys.argv.index("--only") + 1]) if "--only" in sys.argv else None
    cfg = json.load(open(cfg_path))
    base = os.path.dirname(os.path.abspath(cfg_path))
    cfg["_base"] = base
    FONT_OVERRIDES.update(cfg.get("fonts") or {})
    if cfg.get("font"):
        FONT_OVERRIDES.setdefault("heavy", cfg["font"])
    out_dir = os.path.join(base, cfg.get("out_dir", "screenshots/final"))
    sizes = cfg.get("sizes", ["1320x2868"])
    frames = cfg["frames"]
    first = []
    for s in sizes:
        W, H = map(int, s.split("x"))
        wide = None
        if cfg.get("panorama"):
            g = resolve(cfg, {})
            N = len(frames)
            spec = bg_spec(g, 0)
            if spec.get("type") == "mesh" and not isinstance(g.get("background"), dict):
                spec = dict(spec, blobs=[dict(b, at=[b["at"][0] + i, b["at"][1]])
                                         for i in range(N) for b in bg_spec(g, i)["blobs"]])
            wide = add_grain(render_bg(N * W, H, spec, W), g["grain"])
            wide = add_pattern(wide, g.get("pattern"), g, W)
            draw_decor(wide, g.get("panorama_decor"), g, W, H, "back")
            for pd in g.get("panorama_devices") or []:   # phones crossing seams (x in frame units)
                extra_device(wide, pd, g, W, H, x_unit=W)
        d = os.path.join(out_dir, s)
        os.makedirs(d, exist_ok=True)
        # same phone top on every frame (device.sync): measure every text block first
        rs = [resolve(cfg, fr) for fr in frames]
        has_dev = [r["device"]["style"] != "none" and r.get("screenshot") for r in rs]   # text-only frames don't sync
        tops = [text_block(Image.new("RGBA", (W, H)), r, W, H) for r, h in zip(rs, has_dev)
                if h and r.get("text_pos") != "bottom"]
        hbot = [text_block(Image.new("RGBA", (W, H)), r, W, H, y0=0) for r, h in zip(rs, has_dev)
                if h and r.get("text_pos") == "bottom"]
        for i, fr in enumerate(frames, 1):
            if only and i != only:
                continue
            c = resolve(cfg, fr)
            if c["device"].get("sync", True):
                c["_sync_top"] = max(tops) if tops else None
                c["_sync_h"] = max(hbot) if hbot else None
            base_img = wide.crop(((i - 1) * W, 0, i * W, H)) if wide is not None else None
            img = render(c, i - 1, W, H, base_img)
            p = os.path.join(d, f"{i:02d}.png")
            img.save(p)
            print("wrote", p, img.size)
            if s == sizes[0]:
                first.append(img)
    if first and not only:
        th = 900
        thumbs = [im.resize((int(im.width * th / im.height), th), Image.LANCZOS) for im in first]
        gap = 12 if cfg.get("panorama") else 40
        sc = Image.new("RGB", (sum(t.width for t in thumbs) + gap * (len(thumbs) + 1), th + 80), (245, 245, 247))
        x = gap
        for t in thumbs:
            sc.paste(t, (x, 40)); x += t.width + gap
        p = os.path.join(out_dir, "showcase.png")
        sc.save(p); print("wrote", p)
    print("fonts:", {k: os.path.basename(v) for k, v in _font_paths.items() if v})


if __name__ == "__main__":
    main()
