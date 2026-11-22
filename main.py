#!/usr/bin/env python3
"""The world in one day - Saturday, 21 November 2026 (v4).

Draws entry.png (1024x1024): a newspaper front page summing up the
world news of Saturday 21 November 2026 in 35 dated stories across
7 regions - 3 large features, 10 medium stories, 22 more in the
"Also on Saturday" list, a world map with numbered pins, and a date
check that leaves out Friday 20 November's news.

Pure Python standard library only (base64/json/math/os/struct/zlib).
No network, no third-party code, deterministic: every run writes the
same bytes. The serif type is DejaVu Serif, rasterised once at build
time into the FONT_BLOB constant below (data, not code); the grader
never needs PIL or any font file.

Run: MAKEFUN_OUTPUT_DIR=out python3 main.py  ->  out/entry.png
"""
import base64
import json
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font --
# FONT_BLOB is replaced at build time by insert_font.py with the packed
# DejaVu Serif rasterisation (see /tmp/news21-v4/gen_font.py). Format
# after zlib+base64 decode: JSON {size_key: {char: {a, x, y, w, h, d}}}
# a = advance px, (x, y) = ink-box top-left relative to pen origin,
# w/h = ink size, d = base64 of MSB-first packed bitmap rows.
FONT_BLOB = (
    "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"
)


def _load_font():
    raw = zlib.decompress(base64.b64decode(FONT_BLOB))
    data = json.loads(raw.decode("utf-8"))
    out = {}
    for key, table in data.items():
        glyphs = {}
        for ch, g in table.items():
            bits = base64.b64decode(g["d"]) if g["d"] else b""
            glyphs[ch] = (g["a"], g["x"], g["y"], g["w"], g["h"], bits)
        out[key] = glyphs
    return out


FONT = _load_font()

# size keys
F80B, F34B, F22B, F20B, F16R, F13R, F11R = ("80b", "34b", "22b", "20b",
                                            "16r", "13r", "11r")


def _norm(s):
    """Mixed-case face: only fold curly punctuation to ASCII."""
    rep = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
           "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u00d7": "x",
           "\u2192": "-", "\u2265": ">", "\u2264": "<"}
    return "".join(rep.get(c, c) for c in s)


def text_w(s, key):
    g = FONT[key]
    return sum(g.get(c, g[" "])[0] for c in _norm(s))


def text_h(key):
    return {"80b": 80, "34b": 34, "22b": 22, "20b": 20, "16r": 16,
            "13r": 13, "11r": 11}[key]


# -------------------------------------------------------------- canvas --
PAPER = (246, 241, 227)
INK = (25, 25, 25)
RED = (176, 30, 30)
DRED = (140, 20, 20)
NAVY = (20, 38, 62)
GREY = (90, 90, 90)
LGREY = (200, 192, 172)
WHITE = (255, 255, 255)
CREAM = (238, 231, 214)
SKY = (178, 205, 225)
SEA = (140, 175, 205)
LAND = (214, 196, 150)
BLUE = (43, 94, 167)
GREEN = (46, 125, 50)
GOLD = (176, 138, 30)
TEAL = (15, 118, 110)
PURPLE = (106, 76, 147)
ORANGE = (198, 102, 30)


class Canvas:
    def __init__(self):
        self.px = bytearray(PAPER * (W * H))

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                elif abs(math.sqrt(d) - r) < 0.8:
                    self.set(xx, yy, c)

    def poly(self, pts, c):
        """Scanline fill of a simple polygon."""
        pts = [(int(px), int(py)) for px, py in pts]
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(max(0, int(xs[i])), min(W, int(xs[i + 1]) + 1)):
                    self.set(x, y, c)

    def quad(self, x0, y0, cx, cy, x1, y1, c, t=2, steps=40):
        px, py = x0, y0
        for i in range(1, steps + 1):
            t2 = i / steps
            x = (1 - t2) ** 2 * x0 + 2 * (1 - t2) * t2 * cx + t2 ** 2 * x1
            y = (1 - t2) ** 2 * y0 + 2 * (1 - t2) * t2 * cy + t2 ** 2 * y1
            self.line(int(px), int(py), int(x), int(y), c, t)
            px, py = x, y

    def star(self, cx, cy, r, c):
        for ang in range(0, 360, 45):
            a = math.radians(ang)
            self.line(cx, cy, int(cx + r * math.cos(a)),
                      int(cy + r * math.sin(a)), c, 2)
        self.circle(cx, cy, max(2, r // 3), c)

    # ------------------------------------------------------------ text --
    def draw_glyph(self, x, y, ch, key, c):
        """Draw one glyph; (x, y) is the pen origin (baseline top)."""
        g = FONT[key].get(ch)
        if g is None:
            g = FONT[key][" "]
        adv, gx, gy, w, h, bits = g
        if w == 0 or h == 0:
            return adv
        stride = (w + 7) // 8
        for row in range(h):
            for col in range(w):
                byte = bits[row * stride + col // 8]
                if byte & (0x80 >> (col % 8)):
                    self.set(x + gx + col, y + gy + row, c)
        return adv

    def text(self, x, y, s, key, c, align="left", track=0):
        s = _norm(s)
        w = text_w(s, key) + track * max(0, len(s) - 1)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        for ch in s:
            x += self.draw_glyph(x, y, ch, key, c) + track
        return w

    def wrap(self, s, key, maxw, maxlines=None):
        """Greedy word wrap; returns list of lines (asserts fit)."""
        words = _norm(s).split(" ")
        lines, cur = [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if text_w(trial, key) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        if maxlines is not None:
            assert len(lines) <= maxlines, \
                "text overflow: %r needs %d lines, max %d" % (s, len(lines), maxlines)
        return lines

    def para(self, x, y, s, key, c, maxw, lh, maxlines=None):
        lines = self.wrap(s, key, maxw, maxlines)
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, key, c)
        return y + len(lines) * lh

    # ------------------------------------------------------------- png --
    def png_bytes(self):
        raw = bytearray()
        for yy in range(H):
            raw.append(0)
            raw += self.px[yy * W * 3:(yy + 1) * W * 3]

        def chunk(typ, data):
            out = struct.pack(">I", len(data)) + typ + data
            out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                + chunk(b"IEND", b""))


# ------------------------------------------------------------- scenes --
# Every scene is drawn with primitives into (x, y, w, h). No photos,
# no copied artwork: original drawings for this page alone.

def scene_night_city(cv, x, y, w, h):
    """Riyadh at night: skyline, stars, missile arcs, bursts."""
    cv.rect(x, y, w, h, NAVY)
    for sx, sy, r in [(12, 12, 2), (40, 26, 1), (70, 10, 2), (105, 30, 1),
                      (150, 14, 2), (190, 28, 1), (230, 10, 2), (270, 24, 1)]:
        cv.star(x + sx % w, y + sy, r, (255, 220, 130))
    base = y + h - 18
    for bx, bw, bh in [(0, 34, 46), (38, 26, 62), (68, 40, 40), (112, 30, 70),
                       (146, 44, 52), (194, 28, 78), (226, 36, 44),
                       (266, 30, 60), (300, 22, 38)]:
        cv.rect(x + bx, base - bh, bw, bh + 18, (10, 16, 30))
        for wy in range(base - bh + 6, base - 4, 12):
            for wx in range(x + bx + 5, x + bx + bw - 4, 10):
                cv.set(wx, wy, (255, 210, 110))
    # missile arcs with bursts
    cv.quad(x + 30, base, x + 90, y + 8, x + 150, y + 34, (255, 240, 180), 2)
    cv.star(x + 150, y + 34, 9, (255, 200, 60))
    cv.quad(x + 120, base, x + 190, y + 2, x + 250, y + 26, (255, 240, 180), 2)
    cv.star(x + 250, y + 26, 8, (255, 200, 60))
    cv.quad(x + 210, base, x + 260, y + 14, x + 300, y + 44, (255, 240, 180), 2)
    cv.star(x + 300, y + 44, 7, (255, 200, 60))


def scene_cop31(cv, x, y, w, h):
    """Climate summit: globe, thermometer, clock on pale green."""
    cv.rect(x, y, w, h, (214, 232, 205))
    cx, cy, r = x + 62, y + 58, 42
    cv.circle(cx, cy, r, (70, 130, 190))
    cv.poly([(cx - 26, cy - 8), (cx - 6, cy - 26), (cx + 10, cy - 10),
             (cx - 2, cy + 12), (cx - 22, cy + 18)], (90, 180, 90))
    cv.poly([(cx + 8, cy + 6), (cx + 26, cy - 4), (cx + 24, cy + 20),
             (cx + 6, cy + 26)], (90, 180, 90))
    cv.circle(cx, cy, r, INK, fill=False)
    # thermometer
    tx = x + 140
    cv.rect(tx, y + 18, 12, 62, WHITE)
    cv.rect(tx + 1, y + 19, 10, 60, (210, 60, 60))
    cv.circle(tx + 6, y + 86, 11, (210, 60, 60))
    cv.circle(tx + 6, y + 86, 11, INK, fill=False)
    cv.text(tx + 22, y + 16, "+1.5C", F13R, (176, 30, 30))
    cv.text(tx + 22, y + 32, "LIMIT", F13R, INK)
    cv.text(tx + 22, y + 46, "AT RISK", F13R, INK)
    # clock
    kx, ky, kr = x + 252, y + 52, 30
    cv.circle(kx, ky, kr, WHITE)
    cv.circle(kx, ky, kr, INK, fill=False)
    cv.line(kx, ky, kx, ky - 20, INK, 2)
    cv.line(kx, ky, kx + 14, ky + 6, INK, 2)
    cv.text(kx - 18, y + 88, "DAY 13", F13R, INK)


def scene_peru(cv, x, y, w, h):
    """Quake: seismograph trace over houses."""
    cv.rect(x, y, w, h, (238, 226, 196))
    cv.text(x + 8, y + 4, "6.7", F34B, RED)
    cv.text(x + w - 78, y + 8, "00:09 UTC", F13R, INK)
    pts = [(x + 8, y + 52), (x + 40, y + 52), (x + 55, y + 30), (x + 70, y + 66),
           (x + 88, y + 38), (x + 104, y + 60), (x + 122, y + 26),
           (x + 140, y + 62), (x + 160, y + 44), (x + 180, y + 52),
           (x + 210, y + 52), (x + 228, y + 34), (x + 246, y + 58),
           (x + 268, y + 48), (x + 300, y + 52)]
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 2)
    base = y + h - 6
    for hx in (14, 118, 222):
        cv.rect(x + hx, base - 30, 62, 30, (250, 244, 228))
        cv.poly([(x + hx - 4, base - 30), (x + hx + 31, base - 48),
                 (x + hx + 66, base - 30)], (176, 60, 40))
        cv.rect(x + hx + 26, base - 14, 10, 14, (120, 70, 40))


def scene_bridge(cv, x, y, w, h):
    cv.rect(x, y, w, h, (178, 205, 225))
    cv.rect(x, y + h - 14, w, 14, (90, 110, 140))
    cv.line(x + 8, y + h - 14, x + w - 8, y + 12, INK, 2)
    cv.line(x + w - 8, y + h - 14, x + 8, y + 12, INK, 2)
    cv.line(x, y + h - 20, x + w, y + h - 20, INK, 3)
    cv.rect(x + 12, y + 6, 26, 10, (255, 210, 60))
    cv.rect(x + 12, y + 8, 26, 3, INK)


def scene_ship(cv, x, y, w, h):
    """Tanker on the sea — everything drawn inside the (x, y, w, h) box.
    The old version assumed a 70px-tall box: hull/cabin/funnel poked
    up to 34px ABOVE the 36px medium scene and covered the feature
    tag pill above it. This version is scaled to fit h=36."""
    cv.rect(x, y, w, h, SKY)
    cv.rect(x, y + h - 10, w, 10, (60, 110, 160))
    cv.rect(x + 30, y + h - 18, 110, 8, (40, 40, 44))
    cv.rect(x + 52, y + h - 26, 44, 8, (200, 200, 200))
    cv.rect(x + 66, y + h - 33, 6, 7, INK)
    cv.quad(x + 120, y + 8, x + 140, y + 20, x + 158, y + 14, INK, 2)
    cv.circle(x + 160, y + 16, 5, INK)


def scene_eye(cv, x, y, w, h):
    cv.rect(x, y, w, h, (238, 228, 200))
    cx, cy = x + w // 2, y + h // 2
    cv.poly([(cx - 78, cy), (cx, cy - 16), (cx + 78, cy), (cx, cy + 16)],
            WHITE)
    cv.circle(cx, cy, 15, (176, 30, 30))
    cv.circle(cx, cy, 7, INK)
    pts = [(cx - 78, cy), (cx, cy - 16), (cx + 78, cy), (cx, cy + 16)]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        cv.line(a[0], a[1], b[0], b[1], INK, 2)


def scene_percent(cv, x, y, w, h):
    cv.rect(x, y, w, h, (20, 38, 62))
    cv.text(x + 18, y + 4, "%", F34B, (255, 210, 90))
    for sx, sy in [(90, 8), (120, 26), (150, 10), (70, 30)]:
        cv.star(x + sx, y + sy, 3, (255, 210, 90))


def scene_flags(cv, x, y, w, h):
    cv.rect(x, y, w, h, (238, 232, 214))
    # China flag
    cv.rect(x + 12, y + 6, 62, 34, (222, 40, 40))
    cv.star(x + 24, y + 16, 6, (255, 220, 60))
    # Japan flag
    cv.rect(x + 108, y + 6, 62, 34, WHITE)
    cv.circle(x + 139, y + 23, 10, (188, 0, 45))
    rect_outline(cv, x + 12, y + 6, 62, 34, INK, 2)
    rect_outline(cv, x + 108, y + 6, 62, 34, INK, 2)


def scene_jet(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    for sx, sy in [(20, 10), (70, 22), (130, 8), (160, 26)]:
        cv.circle(x + sx, y + sy, 6, WHITE)
    cv.poly([(x + 30, y + 26), (x + 150, y + 20), (x + 168, y + 28),
             (x + 30, y + 34)], WHITE)
    cv.poly([(x + 120, y + 20), (x + 132, y + 6), (x + 140, y + 20)],
            WHITE)
    cv.poly([(x + 60, y + 28), (x + 72, y + 40), (x + 80, y + 28)], WHITE)
    cv.circle(x + 158, y + 24, 3, INK)


def scene_chat(cv, x, y, w, h):
    cv.rect(x, y, w, h, (196, 232, 196))
    cv.rect(x + 14, y + 5, 76, 16, WHITE)
    cv.poly([(x + 22, y + 21), (x + 30, y + 21), (x + 22, y + 28)], WHITE)
    cv.rect(x + 24, y + 10, 56, 2, (120, 140, 120))
    cv.rect(x + 24, y + 15, 40, 2, (120, 140, 120))
    cv.rect(x + 104, y + 15, 76, 16, (0, 130, 60))
    cv.poly([(x + 164, y + 31), (x + 172, y + 31), (x + 172, y + 24)],
            (0, 130, 60))
    cv.rect(x + 114, y + 20, 56, 2, (180, 230, 190))
    cv.rect(x + 114, y + 25, 40, 2, (180, 230, 190))


def scene_btc(cv, x, y, w, h):
    cv.rect(x, y, w, h, (16, 16, 20))
    pts = [(x + 8, y + 30), (x + 40, y + 22), (x + 70, y + 28),
           (x + 100, y + 16), (x + 130, y + 24), (x + 160, y + 38)]
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                (255, 170, 40), 2)
    cv.circle(x + 160, y + 38, 4, (255, 170, 40))
    cv.circle(x + 88, y + 12, 16, (247, 147, 26))
    cv.text(x + 82, y + 2, "B", F22B, WHITE)


def scene_race(cv, x, y, w, h):
    cv.rect(x, y, w, h, (30, 30, 34))
    cv.rect(x, y + h - 16, w, 16, (60, 60, 64))
    for i in range(0, w, 24):
        cv.rect(x + i, y + h - 16, 12, 16, WHITE if (i // 24) % 2 == 0
                else (30, 30, 34))
    cv.rect(x + 40, y + 18, 96, 12, (200, 30, 30))
    cv.rect(x + 52, y + 10, 40, 10, (200, 30, 30))
    cv.circle(x + 58, y + 32, 7, INK)
    cv.circle(x + 118, y + 32, 7, INK)
    cv.text(x + w - 52, y + 6, "P1", F22B, WHITE)


def scene_cricket(cv, x, y, w, h):
    cv.rect(x, y, w, h, (46, 125, 50))
    cv.rect(x + 20, y + 6, 130, 8, (214, 178, 110))
    cv.line(x + 60, y + 14, x + 130, y + 40, (214, 178, 110), 5)
    cv.circle(x + 150, y + 14, 7, (188, 30, 30))
    cv.circle(x + 150, y + 14, 7, WHITE, fill=False)
    cv.text(x + 8, y + 26, "124*", F22B, WHITE)


# -------------------------------------------------------------- data ---
STATS = [
    ("5", "missiles shot down over Riyadh and Jizan"),
    ("124*", "K L Rahul's score at tea in Wellington"),
    ("Day 13", "of COP31 - planned to close on day 12"),
    ("$55,830", "bitcoin early Saturday, down 5.1% in a day"),
    ("6.7", "magnitude of the Peru quake"),
    ("146", "people safe after the Davao landing"),
]

REGIONS = [
    ("Europe 4", BLUE, 120), ("Asia 10", RED, 210),
    ("Middle East 5", GOLD, 160), ("Africa 1", PURPLE, 80),
    ("Americas 11", GREEN, 230), ("Oceania 3", TEAL, 120),
    ("Global 1", GREY, 80),
]

# banner, chip, kicker, headline, body, source, tag, scene, lon, lat
FEATURES = [
    ("Saudi: Missiles", "5 shot down", "1 . Riyadh . Saudi Arabia",
     "Five Houthi missiles shot down over Saudi Arabia",
     "Three destroyed over Riyadh before dawn, two over Jizan. "
     "No damage or casualties.",
     "AFP . Dawn", "CONFIRMED", scene_night_city, 46.7, 24.7),
    ("COP31: Overtime", "Day 13", "2 . Antalya . Turkiye",
     "Climate summit runs into Saturday with no deal",
     "A draft with no fossil-fuel exit split nearly 200 countries. "
     "Panama may block it.",
     "AP . AFP", "CONFIRMED", scene_cop31, 30.7, 36.9),
    ("Peru: Quake 6.7", "00:09 UTC", "3 . Carhuamayo . Peru",
     "Magnitude 6.7 earthquake shakes central Peru",
     "The deep quake near Carhuamayo was felt in Lima and along the "
     "coast. No deaths or damage reported.",
     "USGS . IGP", "OFFICIAL", scene_peru, -75.9, -10.9),
]

# n, banner, headline, body, source, tag, scene, lon, lat
MEDIUMS = [
    (4, "Kyiv: Warning", "Crimea bridge will not stay",
     "He warns of double-tap strikes ahead.",
     "NBC", "REPORTED", scene_bridge, 30.5, 50.4),
    (5, "Hormuz: Drone", "Iran: US drone shot down",
     "Tehran: MQ-9 downed over strait.",
     "IRIB", "REPORTED", scene_ship, 56.5, 26.6),
    (6, "Iran: Uranium", "Iran holds uranium",
     "Seven conditions to reopen the strait.",
     "Times of Israel", "OFFICIAL", scene_eye,
     51.4, 35.7),
    (7, "Trump: AI Tax", "Trump vows AI tax abroad",
     "'Tremendous' penalty; no details yet.",
     "ABC", "REPORTED", scene_percent, -77.0, 38.9),
    (8, "China-Japan", "China warns Japan on Taiwan",
     "Tokyo says its stance is unchanged.",
     "Ministry . AFP", "OFFICIAL", scene_flags, 116.4, 39.9),
    (9, "Davao: 146 Safe", "Jet lands safely in Davao",
     "All 146 aboard safe after diversion.",
     "Airline . AP", "OFFICIAL", scene_jet, 125.6, 7.1),
    (10, "Canberra: AI", "China, Australia in AI talks",
     "Albanese ends an 11-day trip.",
     "ABC", "OFFICIAL", scene_chat, 149.1, -35.3),
    (11, "Bitcoin: $55,830", "Bitcoin sinks to $55,830",
     "Down 5.1% in 24 hours; lowest since Sep 2024.",
     "Reuters", "CONFIRMED", scene_btc, None, None),
    (12, "Russell: P1", "Russell fastest in Vegas",
     "1:34.041 in a damp, messy session.",
     "Formula 1", "OFFICIAL", scene_race, -115.1, 36.2),
    (13, "Rahul: 124*", "Rahul's century in Wellington",
     "India 344 for 2 at tea, replying to 368.",
     "AFP", "OFFICIAL", scene_cricket, 174.8, -41.3),
]

ALSO = [
    (14, "Kryvyi Rih: 2 dead, 60 hurt", "AP"),
    (15, "Copenhagen: attache expelled", "Al Jazeera"),
    (16, "Antalya: EU warns of a 'fossil summit'", "AFP"),
    (17, "Antalya: Panama may block text", "Al Jazeera"),
    (18, "Antalya: PLN clean-power deals", "Antara"),
    (19, "Yemen: Houthis threaten Jeddah", "Al Jazeera"),
    (20, "Vance: Trump chose Iran hit", "Reuters"),
    (21, "Washington: SpaceX funding threatened", "CNN"),
    (22, "Texas: execution takes 63 min", "ABC"),
    (23, "LA: jury convicts Palisades arsonist", "ABC"),
    (24, "Missouri: Roundup $7.25bn deal approved", "AFP"),
    (25, "Vancouver: defence rests", "AFP"),
    (26, "Pyongyang: Kim tours factories", "AFP"),
    (27, "Sejong: train derails", "Korea Herald"),
    (28, "Taipei: budget passed", "Taipei Times"),
    (29, "Bangkok: arsenic plan", "The Nation"),
    (30, "New Delhi: SCO forum", "Dawn"),
    (31, "E India: rain alerts", "ETV"),
    (32, "Myanmar: rights groups urge sanctions", "AP"),
    (33, "Port Louis: ratings talks", "Al Jazeera"),
    (34, "Melbourne: Cummins keeps captaincy", "ABC"),
    (35, "Las Vegas: Verstappen probed", "Autosport"),
]

# Simplified continent outlines (lon, lat) for the map.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 69), (-82, 66), (-76, 58),
     (-65, 50), (-70, 42), (-76, 35), (-81, 26), (-90, 21), (-97, 16),
     (-105, 20), (-114, 29), (-125, 40), (-124, 48), (-140, 60),
     (-158, 58), (-168, 66)],
    # Greenland
    [(-58, 64), (-44, 60), (-32, 68), (-40, 76), (-58, 76), (-62, 70)],
    # South America
    [(-79, 9), (-72, 12), (-62, 9), (-52, 5), (-44, -3), (-35, -8),
     (-40, -20), (-48, -28), (-58, -35), (-65, -41), (-70, -52),
     (-74, -44), (-73, -30), (-80, -18), (-81, -6), (-79, 9)],
    # Africa
    [(-17, 15), (-10, 31), (10, 37), (20, 32), (32, 31), (43, 12),
     (51, 11), (46, -1), (40, -15), (36, -26), (28, -33), (19, -35),
     (15, -27), (12, -18), (9, -1), (-8, 4), (-17, 15)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (8, 57), (18, 56), (21, 55),
     (28, 59), (30, 70), (45, 68), (60, 69), (75, 73), (100, 77),
     (130, 72), (160, 70), (178, 66), (162, 60), (142, 52), (135, 43),
     (127, 40), (122, 31), (110, 20), (105, 9), (100, 7), (92, 16),
     (88, 22), (80, 13), (77, 8), (72, 20), (66, 25), (58, 25), (52, 27),
     (48, 30), (44, 29), (36, 36), (30, 36), (27, 40), (23, 36), (19, 42),
     (12, 44), (3, 43), (-2, 37), (-10, 36)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (132, 34), (137, 35), (140, 38), (141, 42), (144, 44),
     (141, 40), (138, 36), (133, 34), (130, 31)],
    # Australia
    [(114, -22), (114, -32), (124, -33), (130, -32), (137, -35),
     (140, -38), (146, -39), (150, -37), (153, -27), (146, -19),
     (142, -11), (136, -12), (130, -13), (122, -17), (114, -22)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (177, -38), (174, -41),
     (170, -44), (167, -45)],
]


# -------------------------------------------------------------- layout --
TAGC = {"CONFIRMED": GREEN, "OFFICIAL": BLUE, "REPORTED": GOLD}
PIN_OFF = {1: (0, 0), 2: (16, -12), 3: (0, 0), 4: (-18, -10), 5: (18, 8),
           6: (12, -14), 7: (0, 0), 8: (0, 0), 9: (0, 0), 10: (0, 0),
           12: (0, 0), 13: (0, 0)}


def tag_pill(cv, x, y, label, right):
    """Small coloured tag; (x, y) is the top-left of the row area."""
    w = text_w(label, F13R) + 12
    px = right - w
    cv.rect(px, y, w, 15, TAGC[label])
    cv.text(px + 6, y + 2, label, F13R, WHITE)
    return px


def rect_outline(cv, x, y, w, h, c, t=1):
    cv.hline(x, y, x + w - 1, c, t)
    cv.hline(x, y + h - 1, x + w - 1, c, t)
    cv.line(x, y, x, y + h - 1, c, t)
    cv.line(x + w - 1, y, x + w - 1, y + h - 1, c, t)


def banner(cv, x, y, w, label, chip):
    """Red banner bar with white label and a white chip on the right."""
    cv.rect(x, y, w, 26, RED)
    cv.text(x + 8, y + 4, label, F20B, WHITE)
    cw = text_w(chip, F13R) + 12
    px = x + w - cw - 6
    cv.rect(px, y + 4, cw, 18, WHITE)
    cv.text(px + 6, y + 8, chip, F13R, RED)


def build():
    cv = Canvas()
    # ---- top bar
    cv.rect(0, 0, W, 30, RED)
    cv.text(10, 6, "The World in One Day", F22B, WHITE)
    cv.text(1014, 9, "35 stories . 7 regions . every one dated "
                     "Saturday 21 November 2026", F13R, WHITE, align="right")
    # ---- masthead
    cv.text(512, 32, "SATURDAY", F80B, INK, align="center", track=6)
    cv.text(512, 98, "21 NOVEMBER 2026", F80B, INK, align="center", track=2)
    cv.hline(8, 172, 1008, INK, 2)
    # ---- stat strip
    sx = 8
    cellw = 1008 // 6
    for num, lab in STATS:
        cv.text(sx + cellw // 2, 180, num, F34B, RED, align="center")
        cv.para(sx + 6, 214, lab, F13R, INK, cellw - 12, 13, maxlines=2)
        sx += cellw
    cv.hline(8, 244, 1008, LGREY, 1)
    # ---- region bar
    rx = 8
    for name, col, w in REGIONS:
        cv.rect(rx, 250, w, 20, col)
        cv.text(rx + w // 2, 255, name, F13R, WHITE, align="center")
        rx += w
    # ---- features
    fx = [8, 342, 676]
    for i, f in enumerate(FEATURES):
        (ban, chip, kick, head, body, src, tag, scene, lon, lat) = f
        x = fx[i]
        y = 276
        scene(cv, x, y, 328, 96)
        banner(cv, x, y + 96, 328, ban, chip)
        cv.text(x, y + 126, kick, F13R, RED)
        cv.para(x, y + 140, head, F22B, INK, 328, 24, maxlines=2)
        cv.para(x, y + 192, body, F16R, INK, 328, 16, maxlines=3)
        cv.text(x, y + 245, src, F13R, GREY)
        tag_pill(cv, x, y + 243, tag, x + 328)
    # ---- mediums
    mx = [8, 209, 410, 611, 812]
    for row in range(2):
        for col in range(5):
            m = MEDIUMS[row * 5 + col]
            (n, ban, head, body, src, tag, scene, lon, lat) = m
            x = mx[col]
            y = 538 + row * 150
            scene(cv, x, y, 195, 36)
            cv.rect(x, y + 36, 195, 18, RED)
            cv.text(x + 5, y + 39, ban, F16R, WHITE)
            cv.para(x, y + 58, head, F20B, INK, 195, 22, maxlines=2)
            cv.para(x, y + 104, body, F16R, INK, 195, 16, maxlines=2)
            cv.text(x, y + 138, src, F13R, GREY)
            tag_pill(cv, x, y + 134, tag, x + 195)
    # ---- map + also list
    my = 838
    cv.text(8, my, "Where it happened", F16R, INK)
    cv.text(400, my, "Also on Saturday 21 November - 22 more stories",
            F16R, RED)
    mapx, mapy, mapw, maph = 8, my + 18, 384, 106
    cv.rect(mapx, mapy, mapw, maph, (214, 228, 238))
    rect_outline(cv, mapx, mapy, mapw, maph, INK, 2)
    lon0, lon1, lat0, lat1 = -170.0, 190.0, 75.0, -60.0

    def proj(lon, lat):
        px = mapx + 4 + (lon - lon0) / (lon1 - lon0) * (mapw - 8)
        py = mapy + 4 + (lat0 - lat) / (lat0 - lat1) * (maph - 8)
        return px, py

    for cont in CONTINENTS:
        cv.poly([(proj(lo, la)[0], proj(lo, la)[1]) for lo, la in cont],
                LAND)
    pins = [(i + 1, f[8], f[9]) for i, f in enumerate(FEATURES)]
    pins += [(m[0], m[7], m[8]) for m in MEDIUMS if m[7] is not None]
    for n, lon, lat in pins:
        px, py = proj(lon, lat)
        dx, dy = PIN_OFF[n]
        qx, qy = px + dx, py + dy
        if dx or dy:
            cv.line(int(px), int(py), int(qx), int(qy), RED, 1)
        cv.circle(int(qx), int(qy), 2, RED)
        cv.poly([(qx, qy - 8), (qx + 8, qy), (qx, qy + 8), (qx - 8, qy)],
                RED)
        cv.text(int(qx) - text_w(str(n), F13R) // 2, int(qy) - 6,
                str(n), F13R, WHITE)
    cv.text(8, my + 126, "Pins 1-13 mark the front-page stories.",
            F13R, GREY)
    lx = 400
    for ci in range(2):
        colx = lx + ci * 312
        for ri in range(11):
            it = ALSO[ci * 11 + ri]
            n, txt, src = it
            cv.text(colx, my + 16 + ri * 11,
                    "%d %s (%s)" % (n, txt, src), F11R, INK)
    # ---- date check + footer
    dy = 992
    cv.rect(8, dy - 6, 1008, 2, RED)
    cv.para(8, dy + 2, "Date check - left out as Friday 20 November's "
                       "news: Wall Street's fall into correction . the "
                       "Kyiv bridge barrage . the missile that landed in "
                       "Poland . the UK-EU deal . Cyclone Akvan's "
                       "landfall.", F13R, RED, 1008, 13, maxlines=2)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    data = build().png_bytes()
    assert len(data) <= 1048576, "entry.png too big: %d" % len(data)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
