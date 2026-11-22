#!/usr/bin/env python3
"""Draw the 21 November 2026 world-news image.

Pure standard library: the picture is rasterised into an RGB buffer and
encoded as a PNG with zlib + struct, so the grader needs nothing else.
Deterministic: no clock, no randomness, no network, fixed zlib level.

Layout (1024x1024, newspaper front page):
  header masthead + date, then six story panels in a 2x3 grid, each with
  a coloured kicker strip, a small pictogram and short text, then a footer
  strip with two smaller stories and a sources line.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# --- palette ---------------------------------------------------------------
PAPER = (246, 241, 229)
PANEL = (255, 253, 247)
INK = (25, 25, 25)
BODY = (58, 58, 58)
GREY = (110, 110, 105)
RED = (179, 39, 30)
NAVY = (31, 58, 95)
TEAL = (15, 107, 107)
GREEN = (46, 107, 52)
BLUE = (43, 77, 143)
ORANGE = (217, 108, 30)
GOLD = (197, 141, 28)
LIGHT_BLUE = (126, 178, 214)
SEA = (46, 111, 160)
WHITE = (255, 255, 255)
DARK_RED = (139, 26, 20)

# --- 5x7 pixel font --------------------------------------------------------
# Each glyph is 7 rows of 5 bits, written '1' for a set pixel.
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
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01000", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("00100", "00100", "11110", "00100", "00100", "00100", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines = []
    for paragraph in text.split("\n"):
        cur = ""
        for word in paragraph.split(" "):
            trial = (cur + " " + word).strip()
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def filled_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def circle(self, cx, cy, r, color, t=2):
        for dy in range(-r - 1, r + 2):
            for dx in range(-r - 1, r + 2):
                d = (dx * dx + dy * dy) ** 0.5
                if abs(d - r) <= t / 2.0:
                    self._set(cx + dx, cy + dy, color)

    def fill_polygon(self, points, color):
        """Scanline fill for a simple polygon given as [(x, y), ...]."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    nodes.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            nodes.sort()
            for k in range(0, len(nodes) - 1, 2):
                self.fill_rect(int(nodes[k]), y,
                               max(1, int(nodes[k + 1]) - int(nodes[k])), 1,
                               color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT['?'])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def text_centered(self, y, s, scale, color, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        w = text_width(s, scale)
        self.text(x0 + (x1 - x0 - w) // 2, y, s, scale, color)

    def paragraph(self, x, y, s, scale, color, max_w, line_h):
        lines = wrap_text(s, scale, max_w)
        for i, ln in enumerate(lines):
            self.text(x, y + i * line_h, ln, scale, color)
        return y + len(lines) * line_h


# --- pictograms (each drawn inside a ~96x96 box centred on cx, cy) ---------
def pic_chart(c, cx, cy):
    # axes and four falling bars, then a red arrow line down-right
    c.line(cx - 42, cy + 34, cx + 42, cy + 34, INK, 3)
    c.line(cx - 42, cy + 34, cx - 42, cy - 36, INK, 3)
    tops = [-30, -14, 2, 18]
    for i, top in enumerate(tops):
        x = cx - 34 + i * 20
        c.fill_rect(x, cy + top, 12, cy + 34 - (cy + top), RED)
    c.line(cx - 38, cy - 30, cx + 38, cy + 22, DARK_RED, 3)
    c.fill_polygon([(cx + 38, cy + 22), (cx + 24, cy + 14),
                    (cx + 30, cy + 28)], DARK_RED)


def pic_handcuffs(c, cx, cy):
    c.circle(cx - 24, cy + 4, 17, NAVY, 4)
    c.circle(cx + 24, cy + 4, 17, NAVY, 4)
    c.line(cx - 8, cy - 12, cx + 8, cy - 12, NAVY, 3)
    c.filled_circle(cx - 4, cy - 12, 3, NAVY)
    c.filled_circle(cx + 4, cy - 12, 3, NAVY)
    # small star above, the "most wanted" mark
    c.fill_polygon([(cx, cy - 38), (cx + 4, cy - 28), (cx + 14, cy - 28),
                    (cx + 6, cy - 21), (cx + 9, cy - 11), (cx, cy - 17),
                    (cx - 9, cy - 11), (cx - 6, cy - 21), (cx - 14, cy - 28),
                    (cx - 4, cy - 28)], GOLD)


def pic_blast(c, cx, cy):
    # burst of a strike over broken rooftops
    pts = []
    for i in range(12):
        ang = i * 30.0
        r = 40 if i % 2 == 0 else 16
        pts.append((cx + int(r * math.cos(math.radians(ang))),
                    cy - 8 + int(r * math.sin(math.radians(ang)))))
    c.fill_polygon(pts, ORANGE)
    c.fill_polygon([(cx - 34, cy + 34), (cx - 34, cy + 12), (cx - 12, cy + 12),
                    (cx - 12, cy + 34)], INK)
    c.fill_polygon([(cx + 2, cy + 34), (cx + 2, cy + 18), (cx + 34, cy + 18),
                    (cx + 34, cy + 34)], INK)
    c.line(cx - 12, cy + 12, cx - 20, cy + 22, RED, 3)
    c.line(cx + 2, cy + 18, cx + 12, cy + 28, RED, 3)


def pic_ship(c, cx, cy):
    # cargo ship on the sea, smoke rising
    c.fill_polygon([(cx - 42, cy + 8), (cx + 42, cy + 8), (cx + 30, cy + 28),
                    (cx - 30, cy + 28)], NAVY)
    c.fill_rect(cx - 34, cy - 12, 18, 20, RED)
    c.fill_rect(cx - 12, cy - 12, 18, 20, GOLD)
    c.fill_rect(cx + 10, cy - 12, 18, 20, TEAL)
    c.line(cx + 34, cy + 8, cx + 34, cy - 22, INK, 3)
    for dx, dy, r in ((-18, -30, 9), (-4, -38, 11), (10, -28, 8)):
        c.filled_circle(cx + dx, cy + dy, r, GREY)
    c.line(cx - 46, cy + 36, cx + 46, cy + 36, SEA, 3)
    c.line(cx - 38, cy + 42, cx + 38, cy + 42, LIGHT_BLUE, 2)


def pic_globe(c, cx, cy):
    c.circle(cx, cy, 34, GREEN, 3)
    c.line(cx, cy - 34, cx, cy + 34, GREEN, 2)
    c.line(cx - 34, cy, cx + 34, cy, GREEN, 2)
    c.line(cx - 20, cy - 27, cx + 20, cy - 27, GREEN, 2)
    c.line(cx - 20, cy + 27, cx + 20, cy + 27, GREEN, 2)
    c.fill_polygon([(cx - 8, cy - 14), (cx + 2, cy - 18), (cx + 10, cy - 6),
                    (cx + 2, cy + 2), (cx - 6, cy + 8), (cx - 12, cy - 2)],
                   GREEN)
    c.text_centered(cy + 42, "COP31", 2, GREEN, cx - 48, cx + 48)


def pic_crowd(c, cx, cy):
    # heads in two rows, two placards held up
    for dx in (-30, -10, 10, 30):
        c.filled_circle(cx + dx, cy + 14, 9, INK)
    for dx in (-20, 0, 20):
        c.filled_circle(cx + dx, cy - 6, 9, BLUE)
    c.line(cx - 38, cy - 34, cx - 38, cy - 6, INK, 3)
    c.fill_rect(cx - 50, cy - 46, 26, 14, RED)
    c.line(cx + 38, cy - 34, cx + 38, cy - 6, INK, 3)
    c.fill_rect(cx + 26, cy - 46, 26, 14, NAVY)
    c.line(cx - 46, cy + 30, cx + 46, cy + 30, INK, 3)


# --- stories ----------------------------------------------------------------
# (kicker, colour, headline, body, pictogram)
STORIES = [
    ("MARKETS", RED,
     "AI sell-off sinks world markets",
     "The S&P 500 fell 3.7% into correction. The Nasdaq lost 5.3%, "
     "wiping out its 2026 gains, and Tokyo's Nikkei fell 5.1%.",
     pic_chart),
    ("MEXICO", NAVY,
     "'El Chapo Isidro' captured",
     "Mexican troops seized FBI most-wanted cartel boss Fausto Isidro "
     "Meza Flores in Sinaloa. Gun battles followed the raid.",
     pic_handcuffs),
    ("UKRAINE", DARK_RED,
     "Missiles hit Zelenskyy's hometown",
     "A Russian triple-tap strike on Kryvyi Rih killed a boy, 7, and a "
     "paramedic, 20, and wounded about 60 people.",
     pic_blast),
    ("BALTIC SEA", TEAL,
     "Drones set Russian ship ablaze",
     "The sanctioned cargo ship Sparta II caught fire in the Gulf of "
     "Finland and drifted into Finnish waters.",
     pic_ship),
    ("CLIMATE", GREEN,
     "COP31 talks run past deadline",
     "Negotiators in Antalya stayed in overtime, split over fossil fuels "
     "and climate finance for poorer nations.",
     pic_globe),
    ("FRANCE", BLUE,
     "82,500 march over living costs",
     "Largely peaceful protests swept France over the cost of living and "
     "student rights. Turnout fell from last week.",
     pic_crowd),
]

FOOTER = [
    ("ALSO TODAY", "Bred mosquitoes cut dengue by 69%",
     "Wolbachia mosquitoes cut dengue by 69% in a Brazil trial of "
     "5,700 children."),
    ("ALSO TODAY", "Trump's 'Great Powers' post",
     "He paired Yalta 1945 with his Shenzhen summit photo alongside "
     "Xi and Putin."),
]


def draw_panel(c, x, y, w, h, story):
    kicker, colour, headline, body, pic = story
    c.fill_rect(x, y, w, h, PANEL)
    c.rect(x, y, w, h, INK, 2)
    # kicker strip
    c.fill_rect(x + 2, y + 2, w - 4, 30, colour)
    c.text(x + 14, y + 10, kicker, 2, WHITE)
    # pictogram, left column
    pic(c, x + 62, y + 128)
    # text, right of the pictogram
    tx = x + 122
    tw = w - 136
    y_cur = y + 44
    y_cur = c.paragraph(tx, y_cur, headline, 3, INK, tw, 26)
    c.paragraph(tx, y_cur + 8, body, 2, BODY, tw, 18)


def draw():
    c = Canvas(W, H, PAPER)
    # header
    c.text_centered(28, "THE WORLD IN ONE DAY", 4, INK)
    c.text_centered(74, "SATURDAY, 21 NOVEMBER 2026", 3, RED)
    c.fill_rect(24, 114, W - 48, 3, RED)
    c.fill_rect(24, 121, W - 48, 1, INK)
    # six story panels, 2 columns x 3 rows
    pw, ph, gap = 476, 228, 16
    for i, story in enumerate(STORIES):
        px = 24 + (i % 2) * (pw + gap)
        py = 136 + (i // 2) * (ph + gap)
        draw_panel(c, px, py, pw, ph, story)
    # footer: two smaller stories
    fy = 868
    for i, (kick, head, body) in enumerate(FOOTER):
        fx = 24 + i * (pw + gap)
        c.fill_rect(fx, fy, pw, 112, PANEL)
        c.rect(fx, fy, pw, 112, INK, 2)
        c.text(fx + 14, fy + 10, kick, 2, RED)
        y_cur = c.paragraph(fx + 14, fy + 30, head, 2, INK, pw - 28, 18)
        c.paragraph(fx + 14, y_cur + 4, body, 2, BODY, pw - 28, 18)
    # sources line
    c.text_centered(992, "Sources: Reuters, AP, CNN, WSJ, The Times, Yonhap",
                    2, GREY)
    return c


def png_bytes(c):
    raw = bytearray()
    for y in range(c.h):
        raw.append(0)  # filter: none
        raw += c.buf[y * c.w * 3:(y + 1) * c.w * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
