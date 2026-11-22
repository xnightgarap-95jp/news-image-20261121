#!/usr/bin/env python3
"""news-image-20261121 -- The world in one day: Saturday, 21 November 2026.

Draws a 1024x1024 newspaper front page in pure Python (standard library
only) and writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default: out/).

Layout (top to bottom): red masthead bar; big date headline; sub-headline
strip of the three lead stories; a six-number strip; a region bar; three
large feature stories with drawn pictograms; ten medium stories in a 5x2
grid, each with its own pictogram; a simplified world map with numbered
dots plus a 22-item "also on Saturday" list; a DATE CHECK footer naming
Friday 20 November news that was left out; a sources line.

Every story is dated Saturday 21 November 2026: it happened, was first
reported, or developed further on that day. See NEWS.md for the sources
behind each of the 35 stories.
"""

import os
import struct
import zlib
from math import cos, pi, sin

W, H = 1024, 1024

INK = (16, 16, 16)          # near-black text
PAPER = (255, 255, 255)     # page white
RED = (190, 16, 40)         # masthead red
RED_DK = (140, 10, 28)      # darker red for rules
GREY = (238, 238, 236)      # light panel grey
GREY_LN = (190, 190, 186)   # hairlines
BLUE = (24, 64, 140)        # map sea blue (very light)
LAND = (216, 222, 208)      # map land fill
LAND_LN = (120, 128, 112)   # map land outline

# ---------------------------------------------------------------------------
# 5x7 bitmap font, drawn from scratch. Each glyph is 7 rows of 5 bits.
# Only capitals, digits and common punctuation are needed: all page text
# is upper-cased before drawing.
# ---------------------------------------------------------------------------
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}


def _clean_font():
    """Add the three multi-purpose separator glyphs used on the page."""
    FONT['\u00b7'] = ("00000", "00000", "00000", "01100", "01100",
                      "00000", "00000")  # middle dot
    FONT['\u2014'] = ("00000", "00000", "00000", "11111", "00000",
                      "00000", "00000")  # em dash
    FONT['\u00d7'] = ("00000", "10001", "01010", "00100", "01010",
                      "10001", "00000")  # multiplication sign


_clean_font()


def text_w(s, scale):
    """Pixel width of string s rendered at the given scale."""
    return len(s) * 6 * scale - scale


def draw_char(cv, x, y, ch, scale, color, bold=False):
    glyph = FONT.get(ch, FONT[' '])
    for r in range(7):
        row = glyph[r]
        for c in range(5):
            if row[c] == '1':
                for dy in range(scale):
                    for dx in range(scale):
                        cv.set(x + c * scale + dx, y + r * scale + dy, color)
                        if bold and dx + 1 < scale + 1:
                            cv.set(x + c * scale + dx + 1,
                                   y + r * scale + dy, color)


def draw_text(cv, x, y, s, scale, color, bold=False, align='left'):
    """Draw upper-cased text; returns the pixel width drawn."""
    s = s.upper()
    w = text_w(s, scale)
    if align == 'center':
        x -= w // 2
    elif align == 'right':
        x -= w
    cx = x
    for ch in s:
        draw_char(cv, cx, y, ch, scale, color, bold)
        cx += 6 * scale
    return w


def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    words = s.upper().split(' ')
    lines, cur = [], ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------------------
# Canvas: an in-memory RGB image with drawing primitives.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg=PAPER):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def frame(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        """Bresenham line with a square brush of thickness t."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color, t=1):
        x, y, d = r, 0, 1 - r
        while x >= y:
            for px, py in ((cx + x, cy + y), (cx + y, cy + x),
                           (cx - y, cy + x), (cx - x, cy + y),
                           (cx - x, cy - y), (cx - y, cy - x),
                           (cx + y, cy - x), (cx + x, cy - y)):
                self.rect(px - t // 2, py - t // 2, t, t, color)
            y += 1
            if d <= 0:
                d += 2 * y + 1
            else:
                x -= 1
                d += 2 * (y - x) + 1

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def poly(self, pts, color):
        """Filled polygon (scanline fill)."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.set(x, y, color)

    def ellipse(self, cx, cy, rx, ry, color, t=1, a0=0.0, a1=2 * pi):
        steps = 64
        prev = None
        for i in range(steps + 1):
            a = a0 + (a1 - a0) * i / steps
            p = (round(cx + rx * cos(a)), round(cy + ry * sin(a)))
            if prev is not None:
                self.line(prev[0], prev[1], p[0], p[1], color, t)
            prev = p


# ---------------------------------------------------------------------------
# PNG writing (deterministic: fixed compression, no ancillary chunks).
# ---------------------------------------------------------------------------
def _chunk(tag, data):
    out = struct.pack('>I', len(data)) + tag + data
    out += struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', ihdr)
           + _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
           + _chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------------------
# Pictograms. Each draws inside a box (x, y, w, h) in ink/red.
# ---------------------------------------------------------------------------
def pic_globe(cv, x, y, w, h):
    cx, cy, r = x + w // 2, y + h // 2, min(w, h) // 2 - 2
    cv.circle(cx, cy, r, INK, 2)
    cv.ellipse(cx, cy, r, r // 2, INK, 1)
    cv.ellipse(cx, cy, r // 2, r, INK, 1)
    cv.hline(cx - r, cy, 2 * r, INK, 1)


def pic_missile(cv, x, y, w, h):
    # a shield outline with a rising rocket inside it
    pts = [(x + w // 2, y + h - 2), (x + 2, y + h // 3),
           (x + 2, y + 4), (x + w // 2, y + 2),
           (x + w - 2, y + 4), (x + w - 2, y + h // 3)]
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        cv.line(x0, y0, x1, y1, RED, 2)
    cx, cy = x + w // 2, y + h // 2 + 2
    cv.poly([(cx, cy - 16), (cx + 5, cy + 2), (cx - 5, cy + 2)], INK)
    cv.rect(cx - 4, cy + 2, 8, 10, INK)
    cv.poly([(cx - 4, cy + 12), (cx - 9, cy + 18), (cx - 4, cy + 15)], INK)
    cv.poly([(cx + 4, cy + 12), (cx + 9, cy + 18), (cx + 4, cy + 15)], INK)
    cv.line(cx, cy + 18, cx, cy + 24, RED, 2)


def pic_quake(cv, x, y, w, h):
    # seismograph zigzag with a ground crack
    pts = [(x + 2, y + h // 2)]
    steps = [(0.12, 0), (0.20, -14), (0.28, 12), (0.36, -20), (0.44, 16),
             (0.52, -10), (0.60, 6), (0.70, 0), (0.80, 0), (0.90, 0)]
    px, py = x + 2, y + h // 2
    for fx, dy in steps:
        nx = x + int(w * fx)
        ny = y + h // 2 + dy
        cv.line(px, py, nx, ny, INK, 2)
        px, py = nx, ny
    cv.line(px, py, x + w - 2, y + h // 2, INK, 2)
    cv.line(x + w // 3, y + h - 4, x + w // 3 + 8, y + h // 2 + 6, RED, 2)
    cv.line(x + w // 3 + 8, y + h // 2 + 6, x + w // 2, y + h - 4, RED, 2)


def pic_bridge(cv, x, y, w, h):
    cv.hline(x + 2, y + h - 8, w - 4, INK, 2)
    cv.ellipse(x + w // 2, y + h - 8, w // 2 - 4, h // 2 - 4, INK, 2,
               a0=pi, a1=2 * pi)
    for fx in (0.25, 0.5, 0.75):
        px = x + int(w * fx)
        cv.vline(px, y + h // 2, h // 2 - 6, INK, 1)


def pic_drone(cv, x, y, w, h):
    cx, cy = x + w // 2, y + h // 2
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ax, ay = cx + dx * w // 4, cy + dy * h // 4
        cv.line(cx, cy, ax, ay, INK, 2)
        cv.circle(ax, ay, 5, INK, 2)
        cv.hline(ax - 8, ay, 16, INK, 1)
    cv.disc(cx, cy, 5, RED)


def pic_atom(cv, x, y, w, h):
    cx, cy = x + w // 2, y + h // 2
    rx, ry = w // 2 - 3, h // 3
    cv.ellipse(cx, cy, rx, ry, INK, 2)
    cv.ellipse(cx, cy, rx // 2, ry, INK, 2)
    cv.line(cx - rx, cy, cx + rx, cy, INK, 1)
    cv.disc(cx, cy, 4, RED)


def pic_chip(cv, x, y, w, h):
    cv.frame(x + w // 4, y + h // 4, w // 2, h // 2, INK, 2)
    for i in range(3):
        yy = y + h // 4 + 6 + i * 10
        cv.hline(x + w // 4 - 6, yy, 6, INK, 2)
        cv.hline(x + 3 * w // 4, yy, 6, INK, 2)
    draw_text(cv, x + w // 2, y + h // 2 - 7, '$', 2, RED, bold=True,
              align='center')


def pic_flags(cv, x, y, w, h):
    # two small flags side by side: China (red, dotted stars) and Japan
    fw, fh = w // 2 - 4, h // 2
    cv.rect(x + 2, y + h // 4, fw, fh, RED)
    cv.disc(x + 2 + fw // 3, y + h // 4 + fh // 3, 2, (255, 220, 0))
    cv.disc(x + 2 + 2 * fw // 3, y + h // 4 + fh // 3, 1, (255, 220, 0))
    cv.rect(x + w // 2 + 2, y + h // 4, fw, fh, PAPER)
    cv.frame(x + w // 2 + 2, y + h // 4, fw, fh, INK, 1)
    cv.disc(x + w // 2 + 2 + fw // 2, y + h // 4 + fh // 2, 6, RED)


def pic_plane(cv, x, y, w, h):
    cx, cy = x + w // 2, y + h // 2
    cv.poly([(cx - w // 2 + 4, cy), (cx + w // 2 - 8, cy - 5),
             (cx + w // 2 - 2, cy), (cx + w // 2 - 8, cy + 5)], INK)
    cv.poly([(cx - 6, cy - 2), (cx + 2, cy - 16), (cx + 8, cy - 2)], INK)
    cv.poly([(cx - 14, cy + 2), (cx - 8, cy + 14), (cx - 2, cy + 2)], INK)
    cv.line(cx - w // 2 + 4, cy, cx - w // 2 - 2, cy - 8, INK, 2)
    cv.disc(cx + w // 4, cy - 1, 2, RED)


def pic_dome(cv, x, y, w, h):
    cx = x + w // 2
    cv.ellipse(cx, y + h - 10, w // 3, h // 3, INK, 2, a0=pi, a1=2 * pi)
    cv.vline(cx, y + h // 2 - 12, 12, INK, 2)
    cv.disc(cx, y + h // 2 - 14, 2, RED)
    cv.hline(x + 4, y + h - 10, w - 8, INK, 2)
    for fx in (0.25, 0.5, 0.75):
        cv.vline(x + int(w * fx), y + h - 10, 8, INK, 2)
    cv.hline(x + 4, y + h - 2, w - 8, INK, 2)


def pic_bitcoin(cv, x, y, w, h):
    cx, cy, r = x + w // 2, y + h // 2, min(w, h) // 2 - 2
    cv.circle(cx, cy, r, RED, 2)
    draw_text(cv, cx, cy - 7, 'B', 2, RED, bold=True, align='center')


def pic_flag_race(cv, x, y, w, h):
    # chequered flag on a pole
    cv.vline(x + 4, y + 2, h - 4, INK, 2)
    cw, ch = (w - 8) // 4, (h - 8) // 3
    for r in range(3):
        for c in range(4):
            if (r + c) % 2 == 0:
                cv.rect(x + 8 + c * cw, y + 4 + r * ch, cw, ch, INK)


def pic_cricket(cv, x, y, w, h):
    # bat and ball
    cv.line(x + w // 3, y + 6, x + 2 * w // 3, y + h - 8, INK, 3)
    cv.rect(x + 2 * w // 3 - 3, y + h - 16, 7, 10, RED)
    cv.disc(x + w // 4, y + h // 3, 6, RED)
    cv.circle(x + w // 4, y + h // 3, 6, INK, 1)


# ---------------------------------------------------------------------------
# World map: rough continent polygons in an equirectangular box, with
# numbered dots for the 13 pictured stories (Bitcoin is global: no dot).
# ---------------------------------------------------------------------------
MAP_X, MAP_Y, MAP_W, MAP_H = 8, 690, 320, 252


def _lonlat(lon, lat):
    x = MAP_X + (lon + 180.0) / 360.0 * MAP_W
    y = MAP_Y + (75.0 - lat) / 130.0 * MAP_H
    return int(x), int(y)


CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 62), (-75, 58), (-70, 44), (-75, 35), (-80, 26), (-85, 30),
     (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40),
     (-125, 49), (-135, 58), (-155, 58), (-165, 60)],
    # South America
    [(-80, 9), (-72, 11), (-62, 9), (-52, 5), (-44, -3), (-35, -8),
     (-40, -20), (-48, -28), (-55, -35), (-65, -41), (-70, -52),
     (-73, -44), (-72, -30), (-77, -12), (-81, -4), (-80, 4)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (4, 52), (8, 57), (12, 55),
     (18, 56), (21, 59), (28, 60), (30, 70), (40, 68), (44, 66),
     (40, 58), (35, 54), (30, 46), (28, 44), (23, 40), (19, 42),
     (12, 44), (8, 44), (3, 42), (-2, 37), (-9, 37)],
    # Africa
    [(-6, 35), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12),
     (51, 11), (48, 0), (40, -10), (36, -18), (32, -28), (26, -34),
     (19, -35), (15, -27), (12, -18), (9, -1), (9, 4), (-8, 5),
     (-13, 8), (-17, 15), (-17, 21), (-15, 27), (-10, 31)],
    # Asia
    [(35, 36), (44, 39), (50, 40), (54, 38), (60, 37), (66, 38),
     (70, 42), (75, 45), (80, 50), (90, 55), (100, 60), (110, 62),
     (120, 66), (130, 70), (140, 72), (150, 70), (160, 66), (170, 66),
     (178, 65), (170, 60), (162, 56), (158, 52), (150, 59), (142, 54),
     (140, 45), (135, 43), (130, 38), (127, 35), (122, 31), (120, 25),
     (115, 22), (110, 20), (108, 15), (105, 9), (100, 8), (98, 12),
     (95, 16), (92, 21), (88, 22), (85, 20), (80, 15), (77, 8),
     (75, 12), (72, 20), (68, 23), (62, 25), (57, 26), (52, 27),
     (48, 29), (44, 29), (40, 32), (36, 36)],
    # Australia
    [(114, -22), (122, -14), (132, -12), (137, -15), (142, -11),
     (146, -19), (150, -23), (153, -27), (150, -37), (145, -38),
     (140, -38), (135, -35), (130, -32), (124, -33), (116, -35),
     (113, -25)],
]

DOTS = [
    (1, 27.0, 39.0),    # Antalya - COP31 (nudged west of the cluster)
    (2, 45.0, 21.0),    # Riyadh - missiles (nudged south)
    (3, -75.9, -10.9),  # Peru - quake
    (4, 30.5, 50.4),    # Kyiv - warning
    (5, 61.0, 26.0),    # Hormuz - drone (nudged east)
    (6, 54.0, 38.0),    # Tehran - uranium (nudged east)
    (7, -77.0, 38.9),   # Washington - AI tax
    (8, 116.4, 39.9),   # Beijing - China-Japan
    (9, 125.6, 7.1),    # Davao - landing
    (10, 149.1, -35.3),  # Canberra - AI talks
    (12, -115.1, 36.2),  # Las Vegas - Russell
    (13, 170.0, -41.3),  # Wellington - Rahul (nudged west off the edge)
]


def draw_map(cv):
    cv.rect(MAP_X, MAP_Y, MAP_W, MAP_H, (226, 236, 242))
    for poly in CONTINENTS:
        pts = [_lonlat(lon, lat) for lon, lat in poly]
        cv.poly(pts, LAND)
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            cv.line(x0, y0, x1, y1, LAND_LN, 1)
    for num, lon, lat in DOTS:
        x, y = _lonlat(lon, lat)
        cv.disc(x, y, 8, RED)
        cv.circle(x, y, 8, PAPER, 1)
        draw_text(cv, x, y - 3, str(num), 1, PAPER, bold=True,
                  align='center')


# ---------------------------------------------------------------------------
# The 35 stories. Headlines and summaries are written for this page;
# the facts and sources behind each one are listed in NEWS.md.
# ---------------------------------------------------------------------------
FEATURES = [
    ("1", "COP31 RUNS INTO\nOVERTIME", pic_globe,
     "Climate talks in Antalya run past deadline. The draft has no "
     "fossil-fuel exit."),
    ("2", "RIYADH STOPS\nTHREE MISSILES", pic_missile,
     "Saudi defences down 3 Houthi missiles over Riyadh; 2 more over "
     "Jizan."),
    ("3", "PERU SHAKEN BY\n6.7 QUAKE", pic_quake,
     "M6.7 quake 108 km deep near Carhuamayo, felt in Lima. No deaths "
     "reported."),
]

MEDIUM = [
    ("4", "KYIV WARNS THE\nCRIMEA BRIDGE", pic_bridge,
     "NBC: bridge 'will not stay'."),
    ("5", "DRONE DOWNED\nOVER HORMUZ", pic_drone,
     "Iran claims 58th MQ-9."),
    ("6", "IRAN KEEPS ITS\nURANIUM HOME", pic_atom,
     "60% stock stays home."),
    ("7", "TRUMP VOWS TAX\nON AI ABROAD", pic_chip,
     "Tax on firms abroad."),
    ("8", "BEIJING WARNS\nJAPAN ON TAIWAN", pic_flags,
     "Fix words on Taiwan."),
    ("9", "146 SAFE AFTER\nDAVAO LANDING", pic_plane,
     "767 to Davao; all safe."),
    ("10", "CANBERRA AND\nBEIJING TALK AI", pic_dome,
     "New AI safety dialogue."),
    ("11", "BITCOIN SINKS\nTO $55,830", pic_bitcoin,
     "Lowest since Sep 2024."),
    ("12", "RUSSELL FASTEST\nIN LAS VEGAS", pic_flag_race,
     "1:34.041, P1 in practice."),
    ("13", "RAHUL 124* IN\nWELLINGTON", pic_cricket,
     "Tons in all SENA lands."),
]

ALSO = [
    "14 KRYVYI RIH: 2 DEAD, 60+",
    "15 COPENHAGEN: ENVOY OUT",
    "16 ANTALYA: EU WARNS SUMMIT",
    "17 ANTALYA: PANAMA BLOCKS",
    "18 ANTALYA: PLN CLEAN DEALS",
    "19 YEMEN: PORTS THREATENED",
    "20 VANCE: TRUMP CHOSE HIT",
    "21 SPACEX FUNDS THREATENED",
    "22 TEXAS: EXECUTION 63 MIN",
    "23 LA: ARSONIST CONVICTED",
    "24 MISSOURI: ROUNDUP $7.25B",
    "25 VANCOUVER: TRIAL RESTS",
    "26 PYONGYANG: KIM TOURS",
    "27 SEJONG: TRAIN DERAILS",
    "28 TAIPEI: BUDGET PASSES",
    "29 BANGKOK: ARSENIC PLAN",
    "30 NEW DELHI: SCO FORUM",
    "31 E INDIA: RAIN ALERTS",
    "32 MYANMAR: SANCTIONS URGED",
    "33 PORT LOUIS: RATINGS",
    "34 MELBOURNE: CUMMINS STAYS",
    "35 VEGAS: VERSTAPPEN PROBED",
]

NUMBERS = [
    ("35", "STORIES"),
    ("7", "REGIONS"),
    ("3", "MISSILES"),
    ("146", "SAFE IN DAVAO"),
    ("6.7", "PERU QUAKE"),
    ("82,500", "MARCH IN FRANCE"),
]


def build():
    # Fail loudly instead of silently clipping text off the page.
    col2_w = (W - 340 - 12) // 2
    for line in ALSO:
        assert text_w(line, 2) <= col2_w - 4, 'also-list line too wide: %r' % line
    for _num, head, _pic, _sum in MEDIUM:
        for line in head.split('\n'):
            assert text_w(line, 2) <= 188, 'medium headline too wide: %r' % line
    cv = Canvas(W, H)

    # --- red masthead bar -----------------------------------------------
    cv.rect(0, 0, W, 34, RED)
    draw_text(cv, 12, 9, "THE WORLD IN ONE DAY", 3, PAPER, bold=True)
    draw_text(cv, W - 12, 9, "35 STORIES \u00b7 7 REGIONS", 3, PAPER,
              bold=True, align='right')

    # --- big date headline ----------------------------------------------
    draw_text(cv, W // 2, 42, "SATURDAY", 8, INK, bold=True, align='center')
    draw_text(cv, W // 2, 104, "21 NOVEMBER 2026", 6, RED, bold=True,
              align='center')
    cv.hline(60, 148, W - 120, INK, 2)

    # --- sub-headline strip ----------------------------------------------
    draw_text(cv, W // 2, 156,
              "COP31 OVERTIME \u00b7 RIYADH INTERCEPTS 3 MISSILES "
              "\u00b7 PERU 6.7 QUAKE", 2, INK, bold=True, align='center')

    # --- six-number strip -------------------------------------------------
    y0 = 182
    cell_w = (W - 24) // 6
    for i, (num, label) in enumerate(NUMBERS):
        x = 12 + i * cell_w
        cv.frame(x, y0, cell_w - 4, 46, GREY_LN, 1)
        cv.rect(x, y0, cell_w - 4, 46, GREY)
        draw_text(cv, x + (cell_w - 4) // 2, y0 + 4, num, 3, RED, bold=True,
                  align='center')
        draw_text(cv, x + (cell_w - 4) // 2, y0 + 28, label, 1, INK,
                  align='center')

    # --- region bar --------------------------------------------------------
    cv.rect(0, 236, W, 22, INK)
    draw_text(cv, W // 2, 241,
              "EUROPE 5 \u00b7 ASIA 10 \u00b7 MIDDLE EAST 4 \u00b7 AFRICA 1 "
              "\u00b7 AMERICAS 11 \u00b7 OCEANIA 3 \u00b7 GLOBAL 1",
              2, PAPER, bold=True, align='center')

    # --- three features ----------------------------------------------------
    col_w = (W - 24) // 3
    for i, (num, head, pic, summary) in enumerate(FEATURES):
        x = 12 + i * col_w
        y = 268
        cv.disc(x + 16, y + 14, 13, RED)
        draw_text(cv, x + 16, y + 7, num, 2, PAPER, bold=True,
                  align='center')
        pic(cv, x + 40, y, 84, 34)
        hy = y + 40
        for ln, line in enumerate(head.split('\n')):
            draw_text(cv, x + 6, hy + ln * 24, line, 3, INK, bold=True)
        sy = hy + 52
        for ln, line in enumerate(wrap_text(summary, col_w - 24, 2)):
            draw_text(cv, x + 6, sy + ln * 15, line, 2, INK)
        cv.vline(x + col_w - 6, y, 158, GREY_LN, 1)

    # --- medium grid: 5 columns x 2 rows ----------------------------------
    grid_y = 446
    cell_w = (W - 24) // 5
    cell_h = 118
    for idx, (num, head, pic, summary) in enumerate(MEDIUM):
        col, row = idx % 5, idx // 5
        x = 12 + col * cell_w
        y = grid_y + row * cell_h
        cv.frame(x, y, cell_w - 6, cell_h - 8, GREY_LN, 1)
        cv.disc(x + 14, y + 12, 10, RED)
        draw_text(cv, x + 14, y + 6, num, 1, PAPER, bold=True,
                  align='center')
        pic(cv, x + 30, y + 2, 52, 24)
        hy = y + 30
        for ln, line in enumerate(head.split('\n')):
            draw_text(cv, x + 6, hy + ln * 15, line, 2, INK, bold=True)
        sy = hy + 32
        for ln, line in enumerate(wrap_text(summary, cell_w - 18, 2)):
            draw_text(cv, x + 6, sy + ln * 14, line, 2, INK)

    # --- map + also-list ----------------------------------------------------
    draw_map(cv)
    ax = 340
    draw_text(cv, ax, 692, "ALSO ON SATURDAY 21 NOVEMBER", 2, RED,
              bold=True)
    draw_text(cv, ax, 710, "22 MORE STORIES", 2, INK, bold=True)
    cv.hline(ax, 730, W - ax - 12, INK, 2)
    col2_w = (W - ax - 12) // 2
    for i, line in enumerate(ALSO):
        col = i // 11
        row = i % 11
        draw_text(cv, ax + col * col2_w, 742 + row * 19, line, 2, INK)

    # --- DATE CHECK footer ---------------------------------------------------
    cv.hline(12, 952, W - 24, INK, 2)
    dc = ("DATE CHECK \u2014 LEFT OUT: FRIDAY 20 NOV: WALL STREET "
          "CORRECTION, KYIV BRIDGE BARRAGE, POLAND MISSILE, UK-EU DEAL, "
          "CYCLONE AKVAN LANDFALL.")
    for ln, line in enumerate(wrap_text(dc, W - 24, 2)):
        draw_text(cv, 12, 960 + ln * 15, line, 2, INK, bold=True)

    # --- sources line ---------------------------------------------------------
    src = ("SOURCES: AP, REUTERS, AFP, USGS, ESA, ABC NEWS, NBC, "
           "AL JAZEERA, IANS, GLOBAL SECURITY \u00b7 ALL 35 STORIES "
           "DATED SATURDAY 21 NOVEMBER 2026 \u00b7 SEE NEWS.MD")
    draw_text(cv, 12, 1002, src, 1, INK)

    return cv


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', 'out')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'entry.png')
    n = write_png(build(), path)
    print('wrote %s (%d bytes)' % (path, n))


if __name__ == '__main__':
    main()
