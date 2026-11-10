#!/usr/bin/env python3
"""Generate 6 fake iPhone screenshots (1206x2622) so every example config renders out of the box.

  python3 scripts/make_demo_screens.py            # -> examples/raw/01.png ... 06.png
  python3 scripts/make_demo_screens.py out/dir    # custom folder

The UI is a made-up finance/productivity app ("Pocket"); replace with real simulator captures.
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1206, 2622
CANDIDATES = {
    "bold": ["/Library/Fonts/SF-Pro-Display-Bold.otf", "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
             "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "semi": ["/Library/Fonts/SF-Pro-Display-Semibold.otf", "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
             "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "reg": ["/Library/Fonts/SF-Pro-Display-Regular.otf", "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
            "/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
}


def F(kind, size):
    for p in CANDIDATES[kind]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


INK, MUTED, BG, CARD = "#0F1222", "#7A7F93", "#F4F5FA", "#FFFFFF"
BRAND, GREEN, ORANGE, PINK, SKY = "#5B5BF0", "#16A34A", "#F97316", "#E11D48", "#0EA5E9"


def base(title, sub=None):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((70, 150), "9:41", font=F("semi", 46), fill=INK)
    for i in range(4):  # signal bars + battery
        d.rounded_rectangle([930 + i * 26, 190 - i * 12, 946 + i * 26, 190], 4, fill=INK)
    d.rounded_rectangle([1050, 155, 1135, 192], 10, outline=INK, width=4)
    d.rounded_rectangle([1056, 161, 1122, 186], 6, fill=INK)
    if sub:
        d.text((70, 270), sub, font=F("semi", 42), fill=MUTED)
    d.text((70, 330 if sub else 280), title, font=F("bold", 100), fill=INK)
    return im, d


def tabbar(d, active):
    d.rectangle([0, H - 230, W, H], fill=CARD)
    d.line([0, H - 230, W, H - 230], fill="#E6E8F0", width=3)
    for i, name in enumerate(["Home", "Stats", "Goals", "Chat", "Me"]):
        cx = 120 + i * 241
        col = BRAND if i == active else "#A3A8BA"
        d.rounded_rectangle([cx - 34, H - 190, cx + 34, H - 122], 18, fill=col)
        tw = d.textlength(name, font=F("semi", 34))
        d.text((cx - tw / 2, H - 105), name, font=F("semi", 34), fill=col)


def row(d, y, color, title, sub, amount, amount_col=INK):
    d.rounded_rectangle([60, y, W - 60, y + 200], 40, fill=CARD)
    d.ellipse([100, y + 45, 210, y + 155], fill=color)
    d.text((245, y + 52), title, font=F("semi", 50), fill=INK)
    d.text((245, y + 118), sub, font=F("reg", 40), fill=MUTED)
    tw = d.textlength(amount, font=F("semi", 50))
    d.text((W - 100 - tw, y + 75), amount, font=F("semi", 50), fill=amount_col)


def s1_home():
    im, d = base("Hi, Sam", "Good morning")
    d.rounded_rectangle([60, 480, W - 60, 1010], 56, fill=BRAND)
    d.text((115, 560), "Total balance", font=F("semi", 46), fill="#C9CBFF")
    d.text((115, 640), "$12,480.20", font=F("bold", 128), fill="white")
    d.rounded_rectangle([115, 850, 440, 950], 50, fill="#7A7AF5")
    d.text((165, 873), "+ Add money", font=F("semi", 42), fill="white")
    d.rounded_rectangle([470, 850, 760, 950], 50, fill="#7A7AF5")
    d.text((530, 873), "Send", font=F("semi", 42), fill="white")
    d.text((70, 1080), "Recent", font=F("bold", 64), fill=INK)
    data = [(GREEN, "Salary", "Today, 09:12", "+$3,200", GREEN), (ORANGE, "Coffee Lab", "Yesterday", "-$4.80", INK),
            (PINK, "Gym Club", "Mon", "-$39.00", INK), (SKY, "Groceries", "Sun", "-$86.15", INK),
            (BRAND, "Savings", "Sat", "+$250", GREEN)]
    for k, r in enumerate(data):
        row(d, 1190 + k * 230, *r)
    tabbar(d, 0)
    return im


def s2_stats():
    im, d = base("Insights", "November")
    d.rounded_rectangle([60, 480, W - 60, 1280], 56, fill=CARD)
    d.text((115, 540), "Spent this month", font=F("semi", 44), fill=MUTED)
    d.text((115, 600), "$1,842", font=F("bold", 110), fill=INK)
    vals = [0.45, 0.7, 0.38, 0.9, 0.62, 0.55, 0.8]
    for i, v in enumerate(vals):
        x = 130 + i * 140
        h = 420 * v
        d.rounded_rectangle([x, 1200 - h, x + 80, 1200], 26, fill=BRAND if i == 3 else "#D9DAFF")
    cats = [(ORANGE, "Food & drinks", "32%", "$590"), (SKY, "Transport", "18%", "$332"),
            (PINK, "Health", "12%", "$221"), (GREEN, "Shopping", "24%", "$442")]
    for k, (c, t, p, a) in enumerate(cats):
        row(d, 1360 + k * 230, c, t, p + " of spending", a)
    tabbar(d, 1)
    return im


def s3_goals():
    im, d = base("Goals", "3 active")
    goals = [(GREEN, "New laptop", 0.72, "$1,440 / $2,000"), (ORANGE, "Trip to Lisbon", 0.45, "$675 / $1,500"),
             (PINK, "Emergency fund", 0.88, "$4,400 / $5,000"), (SKY, "Bike", 0.2, "$120 / $600")]
    for k, (c, t, p, a) in enumerate(goals):
        y = 500 + k * 440
        d.rounded_rectangle([60, y, W - 60, y + 400], 48, fill=CARD)
        d.ellipse([110, y + 60, 230, y + 180], fill=c)
        d.text((265, y + 70), t, font=F("bold", 58), fill=INK)
        d.text((265, y + 140), a, font=F("reg", 42), fill=MUTED)
        d.rounded_rectangle([110, y + 260, W - 110, y + 310], 25, fill="#ECEDF5")
        d.rounded_rectangle([110, y + 260, 110 + (W - 220) * p, y + 310], 25, fill=c)
        d.text((W - 230, y + 70), f"{int(p * 100)}%", font=F("bold", 58), fill=c)
    tabbar(d, 2)
    return im


def s4_chat():
    im, d = base("Assistant", "Ask anything")
    bubbles = [("me", "How much did I spend on\ncoffee this month?"),
               ("ai", "You spent $62.40 on coffee\nin November, 18% less\nthan October."),
               ("me", "Set a $50 limit for December"),
               ("ai", "Done! I'll nudge you when\nyou reach $40.")]
    y = 520
    for who, txt in bubbles:
        lines = txt.split("\n")
        bh = 60 + 70 * len(lines)
        bw = max(d.textlength(l, font=F("semi", 48)) for l in lines) + 100
        x0 = W - 70 - bw if who == "me" else 70
        d.rounded_rectangle([x0, y, x0 + bw, y + bh], 44, fill=BRAND if who == "me" else CARD)
        for i, l in enumerate(lines):
            d.text((x0 + 50, y + 35 + i * 70), l, font=F("semi", 48), fill="white" if who == "me" else INK)
        y += bh + 50
    d.rounded_rectangle([60, H - 400, W - 60, H - 270], 65, fill=CARD)
    d.text((120, H - 365), "Message...", font=F("reg", 46), fill=MUTED)
    d.ellipse([W - 190, H - 390, W - 80, H - 280], fill=BRAND)
    tabbar(d, 3)
    return im


def s5_cards():
    im, d = base("Cards", "2 cards")
    for k, (c1, c2, name, num) in enumerate([(BRAND, "#9B6BFF", "Everyday", "•••• 4821"),
                                            ("#111827", "#374151", "Travel", "•••• 0937")]):
        y = 480 + k * 620
        card = Image.new("RGB", (W - 120, 560), c1)
        cd = ImageDraw.Draw(card)
        for i in range(W - 120):
            t = i / (W - 120)
            col = tuple(int(int(c1[j:j + 2], 16) * (1 - t) + int(c2[j:j + 2], 16) * t) for j in (1, 3, 5))
            cd.line([i, 0, i, 560], fill=col)
        m = Image.new("L", card.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, card.width - 1, 559], 56, fill=255)
        im.paste(card, (60, y), m)
        d.text((120, y + 60), name, font=F("semi", 52), fill="white")
        d.text((120, y + 400), num, font=F("bold", 70), fill="white")
        d.rounded_rectangle([W - 300, y + 60, W - 130, y + 170], 24, fill="#FFFFFF55")
    d.text((70, 1760), "Controls", font=F("bold", 64), fill=INK)
    for k, (t, on) in enumerate([("Freeze card", False), ("Online payments", True)]):
        y = 1870 + k * 220
        d.rounded_rectangle([60, y, W - 60, y + 190], 40, fill=CARD)
        d.text((110, y + 65), t, font=F("semi", 52), fill=INK)
        d.rounded_rectangle([W - 270, y + 55, W - 110, y + 135], 40, fill=GREEN if on else "#D5D8E3")
        cx = W - 150 if on else W - 230
        d.ellipse([cx - 34, y + 61, cx + 34, y + 129], fill="white")
    tabbar(d, 4)
    return im


def s6_profile():
    im, d = base("Profile")
    d.ellipse([W / 2 - 150, 470, W / 2 + 150, 770], fill="#FFB86B")
    tw = d.textlength("Sam Rivera", font=F("bold", 72))
    d.text(((W - tw) / 2, 810), "Sam Rivera", font=F("bold", 72), fill=INK)
    tw = d.textlength("Member since 2024", font=F("reg", 44))
    d.text(((W - tw) / 2, 910), "Member since 2024", font=F("reg", 44), fill=MUTED)
    for k, (v, l) in enumerate([("128", "Days streak"), ("$3.2k", "Saved"), ("12", "Goals")]):
        x = 60 + k * 365
        d.rounded_rectangle([x, 1020, x + 335, 1250], 40, fill=CARD)
        tw = d.textlength(v, font=F("bold", 72))
        d.text((x + (335 - tw) / 2, 1060), v, font=F("bold", 72), fill=BRAND)
        tw = d.textlength(l, font=F("reg", 38))
        d.text((x + (335 - tw) / 2, 1170), l, font=F("reg", 38), fill=MUTED)
    for k, (c, t) in enumerate([(BRAND, "Notifications"), (GREEN, "Security & Face ID"), (ORANGE, "Export data"),
                                (SKY, "Appearance"), (PINK, "Help & support")]):
        y = 1310 + k * 200
        d.rounded_rectangle([60, y, W - 60, y + 175], 36, fill=CARD)
        d.rounded_rectangle([100, y + 42, 190, y + 132], 24, fill=c)
        d.text((230, y + 58), t, font=F("semi", 52), fill=INK)
        d.text((W - 140, y + 50), "›", font=F("bold", 70), fill=MUTED)
    tabbar(d, 4)
    return im


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "examples", "raw")
    os.makedirs(out, exist_ok=True)
    for i, fn in enumerate([s1_home, s2_stats, s3_goals, s4_chat, s5_cards, s6_profile], 1):
        p = os.path.join(out, f"{i:02d}.png")
        fn().save(p)
        print("wrote", os.path.normpath(p))


if __name__ == "__main__":
    main()
