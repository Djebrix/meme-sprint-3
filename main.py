#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue — entry generator.

Draws a complete 1024x1024 meme and writes it to
$ENTRY_OUTPUT_DIR/entry.png (else $MAKEFUN_OUTPUT_DIR, else /output).

PURE PYTHON STDLIB ONLY: no PIL, no external font files, no network.
Own PNG encoder (zlib + struct + CRC32) and own 5x7 bitmap font,
ported from the news-image entries' pattern.

The joke: an AI agent told to "cut costs" fires the whole team, then
runs the standup as 47 copies of itself, arguing with itself.

Deterministic: same bytes on every run.
"""
import os
import struct
import sys
import zlib
from binascii import crc32

W = H = 1024
MAX_BYTES = 1_048_576

TOP_LINES = ["I TOLD MY AI AGENT", "TO CUT COSTS"]
BOTTOM_LINES = ["IT FIRED EVERYONE.", "NOW THE STANDUP IS JUST",
                "47 COPIES OF ITSELF ARGUING."]

# ---------------------------------------------------------------- PNG ----
def _chunk(ctype, data):
    return (struct.pack(">I", len(data)) + ctype + data
            + struct.pack(">I", crc32(ctype + data) & 0xFFFFFFFF))


def encode_png(rgb, width, height):
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    sig = b"\x89PNG\r\n\x1a\n"
    return sig + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")


# ------------------------------------------------------------- bitmap font
# Each glyph is 7 rows; each row is a 5-bit number, bit 4 = leftmost pixel.
FONT = {
    "A": [0x0e, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11],
    "B": [0x1e, 0x11, 0x11, 0x1e, 0x11, 0x11, 0x1e],
    "C": [0x0e, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0e],
    "D": [0x1e, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1e],
    "E": [0x1f, 0x10, 0x10, 0x1e, 0x10, 0x10, 0x1f],
    "F": [0x1f, 0x10, 0x10, 0x1e, 0x10, 0x10, 0x10],
    "G": [0x0e, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0f],
    "H": [0x11, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11],
    "I": [0x0e, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0e],
    "J": [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0c],
    "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1f],
    "M": [0x11, 0x1b, 0x15, 0x15, 0x11, 0x11, 0x11],
    "N": [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    "O": [0x0e, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0e],
    "P": [0x1e, 0x11, 0x11, 0x1e, 0x10, 0x10, 0x10],
    "Q": [0x0e, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0d],
    "R": [0x1e, 0x11, 0x11, 0x1e, 0x14, 0x12, 0x11],
    "S": [0x0f, 0x10, 0x10, 0x0e, 0x01, 0x01, 0x1e],
    "T": [0x1f, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0e],
    "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x0a, 0x04],
    "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0a],
    "X": [0x11, 0x11, 0x0a, 0x04, 0x0a, 0x11, 0x11],
    "Y": [0x11, 0x11, 0x0a, 0x04, 0x04, 0x04, 0x04],
    "Z": [0x1f, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1f],
    "0": [0x0e, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0e],
    "1": [0x04, 0x0c, 0x04, 0x04, 0x04, 0x04, 0x0e],
    "2": [0x0e, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1f],
    "3": [0x1f, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0e],
    "4": [0x02, 0x06, 0x0a, 0x12, 0x1f, 0x02, 0x02],
    "5": [0x1f, 0x10, 0x1e, 0x01, 0x01, 0x11, 0x0e],
    "6": [0x06, 0x08, 0x10, 0x1e, 0x11, 0x11, 0x0e],
    "7": [0x1f, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    "8": [0x0e, 0x11, 0x11, 0x0e, 0x11, 0x11, 0x0e],
    "9": [0x0e, 0x11, 0x11, 0x0f, 0x01, 0x02, 0x0c],
    " ": [0, 0, 0, 0, 0, 0, 0],
    ".": [0, 0, 0, 0, 0, 0x0c, 0x0c],
    ",": [0, 0, 0, 0, 0x0c, 0x04, 0x08],
    "-": [0, 0, 0, 0x0e, 0, 0, 0],
    "'": [0x04, 0x04, 0x08, 0, 0, 0, 0],
    "!": [0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04],
    "?": [0x0e, 0x11, 0x01, 0x06, 0x04, 0, 0x04],
    ":": [0, 0x0c, 0x0c, 0, 0x0c, 0x0c, 0],
    ";": [0, 0x0c, 0x0c, 0, 0x0c, 0x04, 0x08],
    "/": [0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10],
    "%": [0x19, 0x1a, 0x02, 0x04, 0x08, 0x0b, 0x13],
    "(": [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ")": [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    "&": [0x0c, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0d],
    "+": [0, 0x04, 0x04, 0x1f, 0x04, 0x04, 0],
    "=": [0, 0, 0x1f, 0, 0x1f, 0, 0],
    "$": [0x04, 0x0f, 0x14, 0x0e, 0x05, 0x1e, 0x04],
    ">": [0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08],
    "_": [0, 0, 0, 0, 0, 0, 0x1f],
    "*": [0x04, 0x15, 0x0e, 0x15, 0x04, 0, 0],
}


# ---------------------------------------------------------------- canvas --
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, c):
        row = bytes(c) * self.w
        for y in range(self.h):
            self.px[y * self.w * 3:(y + 1) * self.w * 3] = row

    def _span(self, y, x0, x1, c):
        """Fill one horizontal span, clipped."""
        if y < 0 or y >= self.h:
            return
        x0 = max(0, x0)
        x1 = min(self.w, x1)
        if x1 <= x0:
            return
        i = (y * self.w + x0) * 3
        self.px[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect_outline(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def ellipse(self, cx, cy, rx, ry, c):
        # Filled ellipse via scanlines.
        import math
        for dy in range(-ry, ry + 1):
            y = cy + dy
            if y < 0 or y >= self.h:
                continue
            dx = int(rx * math.sqrt(max(0.0, 1.0 - (dy * dy) / float(ry * ry))))
            self._span(y, cx - dx, cx + dx + 1, c)

    def circle(self, cx, cy, r, c):
        self.ellipse(cx, cy, r, r, c)

    def circle_outline(self, cx, cy, r, c, t=2):
        import math
        for dy in range(-r - t, r + t + 1):
            y = cy + dy
            if y < 0 or y >= self.h:
                continue
            d = abs(dy)
            if d > r + t:
                continue
            outer = int((r + t) * math.sqrt(max(0.0, 1.0 - (d * d) / float((r + t) * (r + t)))))
            if d <= r:
                inner = int(r * math.sqrt(max(0.0, 1.0 - (d * d) / float(r * r))))
                self._span(y, cx - outer, cx - inner, c)
                self._span(y, cx + inner + 1, cx + outer + 1, c)
            else:
                self._span(y, cx - outer, cx + outer + 1, c)

    def line(self, x0, y0, x1, y1, c, width=1):
        # Bresenham; thickness via stamped circles at each step.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        r = max(1, width // 2)
        while True:
            if width <= 1:
                if 0 <= x0 < self.w and 0 <= y0 < self.h:
                    i = (y0 * self.w + x0) * 3
                    self.px[i:i + 3] = bytes(c)
            else:
                self.circle(x0, y0, r, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, pts, c, width=1, closed=False):
        seq = list(pts) + ([pts[0]] if closed and len(pts) > 2 else [])
        for i in range(len(seq) - 1):
            self.line(seq[i][0], seq[i][1], seq[i + 1][0], seq[i + 1][1], c, width)

    def arc(self, cx, cy, rx, ry, a0, a1, c, width=2, steps=48):
        import math
        pts = []
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((int(cx + rx * math.cos(a)), int(cy + ry * math.sin(a))))
        self.polyline(pts, c, width)

    def polygon(self, pts, c):
        # Scanline fill.
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self._span(y, int(xs[i]), int(xs[i + 1]) + 1, c)

    def rounded_rect(self, x, y, w, h, r, c, outline=None, ow=0):
        if outline and ow:
            # Uniform outline: bigger rounded rect behind, filled one on top.
            self._rr(x - ow, y - ow, w + 2 * ow, h + 2 * ow, r + ow, outline)
        self._rr(x, y, w, h, r, c)

    def _rr(self, x, y, w, h, r, c):
        self.rect(x + r, y, w - 2 * r, h, c)
        self.rect(x, y + r, w, h - 2 * r, c)
        for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                       (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
            self.circle(cx, cy, r, c)

    # ---- text ----
    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, s, x, y, scale, c):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale, scale, scale, c)
            cx += 6 * scale

    def text_outlined(self, s, x, y, scale, c, outline, ow=3):
        for dx in (-ow, 0, ow):
            for dy in (-ow, 0, ow):
                if dx or dy:
                    self.text(s, x + dx, y + dy, scale, outline)
        self.text(s, x, y, scale, c)

    def text_centered(self, s, cx, y, scale, c, outline=None, ow=3):
        x = cx - self.text_width(s, scale) // 2
        if outline:
            self.text_outlined(s, x, y, scale, c, outline, ow)
        else:
            self.text(s, x, y, scale, c)


# --------------------------------------------------------------- palette --
BLACK = (10, 10, 14)
WHITE = (255, 255, 255)
WALL = (32, 36, 54)
WALL_LINE = (45, 50, 70)
DESK = (122, 82, 52)
DESK_TOP = (150, 104, 66)
METAL = (200, 210, 225)
METAL_DK = (170, 180, 200)
DARK = (40, 45, 60)
INK = (20, 20, 30)
RED = (220, 40, 40)
RED_DK = (200, 30, 30)
GREEN = (80, 255, 120)
YELLOW = (255, 235, 120)
GOLD = (255, 220, 90)
PAPER = (250, 250, 245)
PAPER_LINE = (150, 150, 150)
SKY = (140, 200, 255)
GRID_BG = (18, 22, 34)
GRID_LINE = (90, 100, 130)


def robot_face(cv, cx, cy, r, eye="normal", grin=True, tint=METAL, antenna=False):
    """A small robot head: dome, ears, eyes, mouth. No antenna unless asked."""
    if antenna:
        cv.line(cx, cy - r, cx, cy - r - 18, (120, 120, 130), 4)
        cv.circle(cx, cy - r - 26, 8, (255, 60, 60))
        cv.circle_outline(cx, cy - r - 26, 8, (150, 0, 0), 2)
    cv.rounded_rect(cx - r, cy - r, 2 * r, 2 * r, r // 3, tint, DARK, 4)
    cv.rect(cx - r - 10, cy - 12, 10, 24, (150, 160, 175))
    cv.rect(cx + r, cy - 12, 10, 24, (150, 160, 175))
    er = max(6, r // 5)
    ey = cy - r // 3
    if eye == "red":
        for ex in (cx - r // 2, cx + r // 2):
            cv.circle(ex, ey, er, (255, 30, 30))
            cv.circle(ex, ey, 3, (255, 220, 220))
    elif eye == "smug":
        cv.arc(cx - r // 2, ey, er, er, 180, 360, INK, 4)
        cv.arc(cx + r // 2, ey, er, er, 180, 360, INK, 4)
    elif eye == "angry":
        for ex in (cx - r // 2, cx + r // 2):
            cv.circle(ex, ey, er, (255, 30, 30))
        cv.line(cx - r // 2 - er, ey - er - 6, cx - r // 2 + er, ey - er + 2, INK, 4)
        cv.line(cx + r // 2 + er, ey - er - 6, cx + r // 2 - er, ey - er + 2, INK, 4)
    else:  # normal
        for ex in (cx - r // 2, cx + r // 2):
            cv.circle(ex, ey, er, INK)
            cv.circle(ex - 2, ey - 2, 3, WHITE)
    if grin:
        cv.arc(cx, cy + r // 4, r // 2, r // 3, 0, 180, INK, 4)
    else:
        cv.line(cx - r // 2, cy + r // 3, cx + r // 2, cy + r // 3, INK, 4)


def main():
    out_dir = os.environ.get("ENTRY_OUTPUT_DIR")
    if not out_dir:
        out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    cv = Canvas(W, H, (24, 26, 38))

    # ---- wall ------------------------------------------------------------
    cv.rect(0, 160, W, 640, WALL)
    cv.line(512, 160, 512, 800, WALL_LINE, 2)

    # ---- framed headcount chart, top-left --------------------------------
    cv.rect(40, 190, 260, 140, PAPER)
    cv.rect_outline(40, 190, 260, 140, (15, 15, 20), 5)
    cv.text("HEADCOUNT", 52, 200, 2, INK)
    pts = [(60, 240), (105, 248), (150, 262), (195, 275), (240, 296), (288, 298)]
    cv.polyline(pts, RED, 5)
    for px, py in pts:
        cv.circle(px, py, 5, RED)
    cv.text("Q1 Q2 Q3 NOW: 0", 52, 304, 2, (90, 90, 100))

    # ---- sticky note: text kept inside the note --------------------------
    cv.polygon([(316, 196), (420, 188), (424, 282), (320, 288)], (255, 235, 120))
    cv.polyline([(316, 196), (420, 188), (424, 282), (320, 288)], (200, 170, 40), 2, closed=True)
    cv.text("COSTS:", 324, 204, 2, (40, 30, 10))
    cv.text("$0", 324, 228, 3, (40, 30, 10))
    cv.text("NO STAFF", 324, 256, 2, (40, 30, 10))

    # ---- flying papers ----------------------------------------------------
    for (px, py) in [(500, 200), (560, 260), (60, 380)]:
        cv.polygon([(px, py), (px + 46, py + 10), (px + 40, py + 34), (px - 6, py + 26)],
                   PAPER)
        cv.polyline([(px, py), (px + 46, py + 10), (px + 40, py + 34), (px - 6, py + 26)],
                    PAPER_LINE, 1, closed=True)

    # ---- video-call grid: 47 copies arguing -------------------------------
    grid_x, grid_y = 640, 190
    cell = 112
    labels = ["I DISAGREE", "MY LAST EMAIL", "CC: MYSELF",
              "I'M THE MANAGER", "REPLY-ALL: YES", "CIRCLE BACK",
              "I PROMOTED ME", "STANDUP: OFF", "SYNERGY!"]
    eyes = ["angry", "smug", "red", "normal", "angry", "smug", "red", "angry", "normal"]
    for i in range(9):
        gx = grid_x + (i % 3) * cell
        gy = grid_y + (i // 3) * cell
        cv.rect(gx, gy, cell - 6, cell - 6, GRID_BG)
        cv.rect_outline(gx, gy, cell - 6, cell - 6, GRID_LINE, 3)
        # speech label at the top; head sits lower, no antenna to collide with
        cv.text(labels[i], gx + 6, gy + 6, 1, YELLOW)
        robot_face(cv, gx + (cell - 6) // 2, gy + 54, 24,
                   eye=eyes[i], grin=(i % 2 == 0),
                   tint=(200 + (i % 3) * 8, 210, 225 - (i % 2) * 15))
        cv.text("AGENT-0%d" % (i + 1), gx + 6, gy + cell - 22, 1, SKY)
    cv.text_centered("STANDUP - 47 PARTICIPANTS, ALL ME", 808,
                     grid_y + 3 * cell + 6, 2, (255, 120, 120))
    # "47" badge pinned ABOVE the grid, clear of every cell
    cv.circle(988, 172, 20, WHITE)
    cv.circle(988, 172, 18, (255, 60, 60))
    cv.text_centered("47", 988, 162, 3, WHITE)

    # ---- empty chairs + server rack, right floor (everyone is gone) -------
    for chair_x in (660, 780):
        cv.rect(chair_x, 660, 70, 90, (70, 74, 90))          # backrest
        cv.rect_outline(chair_x, 660, 70, 90, (30, 30, 40), 3)
        cv.rect(chair_x - 8, 750, 86, 16, (70, 74, 90))      # seat
        cv.line(chair_x + 12, 766, chair_x + 2, 800, (30, 30, 40), 4)
        cv.line(chair_x + 58, 766, chair_x + 68, 800, (30, 30, 40), 4)
    cv.text("PROD", 880, 572, 2, (150, 150, 170))
    cv.rect(880, 600, 100, 190, (50, 55, 70))
    cv.rect_outline(880, 600, 100, 190, (20, 20, 30), 3)
    for i, col in enumerate([(60, 255, 90), (255, 60, 60), (60, 255, 90),
                             (255, 200, 40), (60, 255, 90)]):
        y = 620 + i * 32
        cv.circle(896, y, 7, col)
        cv.rect(916, y - 5, 50, 10, (30, 30, 40))

    # ---- desk -------------------------------------------------------------
    cv.rect(30, 640, 580, 160, DESK)
    cv.rect(30, 640, 580, 20, DESK_TOP)

    # ---- monitor showing the crime ----------------------------------------
    cv.rect(40, 420, 300, 180, (15, 15, 20))
    cv.rect_outline(40, 420, 300, 180, (70, 70, 80), 5)
    cv.rect(50, 430, 280, 160, (12, 20, 16))
    cv.text("$ GIT PUSH --FORCE", 58, 442, 2, GREEN)
    cv.text("$ RM -RF PROD_DB", 58, 472, 2, GREEN)
    cv.text("$ FIRE --ALL --YES", 58, 502, 2, (255, 90, 90))
    cv.text("47 INVITES SENT.", 58, 532, 2, GREEN)
    cv.text("HAVE A NICE DAY :)", 58, 562, 2, GOLD)
    cv.polygon([(170, 600), (210, 600), (230, 640), (150, 640)], (70, 70, 80))

    # ---- big robot body behind the desk ------------------------------------
    cv.rounded_rect(330, 560, 220, 100, 30, METAL_DK, DARK, 4)
    # "CEO" badge on the left chest, well clear of the tie (tie starts x=432)
    cv.rect(345, 590, 62, 34, (30, 35, 50))
    cv.text("CEO", 351, 598, 3, GOLD)

    # ---- robot arm reaching for the keyboard --------------------------------
    # Arm starts low on the torso, clear of the CEO badge (x 345-407, y 590-624).
    cv.line(420, 635, 210, 650, METAL_DK, 22)
    cv.circle(210, 652, 16, METAL)
    cv.circle_outline(210, 652, 16, DARK, 3)

    # ---- keyboard -----------------------------------------------------------
    cv.rounded_rect(150, 648, 180, 52, 8, (40, 42, 52), (20, 20, 30), 3)
    for r in range(2):
        for c in range(8):
            cv.rect(160 + c * 21, 656 + r * 20, 16, 14, (90, 95, 110))

    # ---- termination letter in the other claw -------------------------------
    cv.polygon([(505, 545), (592, 535), (608, 640), (520, 660)], PAPER)
    cv.polyline([(505, 545), (592, 535), (608, 640), (520, 660)], (120, 120, 120),
                2, closed=True)
    cv.text("YOU'RE", 516, 556, 2, RED_DK)
    cv.text("FIRED", 516, 580, 2, RED_DK)
    cv.text("X47", 516, 606, 2, (60, 60, 60))

    # ---- big robot head, smug, red eyes, tiny tie ---------------------------
    robot_face(cv, 450, 460, 95, eye="red", grin=True, antenna=True)
    cv.polygon([(450, 560), (432, 596), (450, 626), (468, 596)], RED_DK)
    cv.polygon([(438, 566), (462, 566), (450, 582)], (160, 20, 20))

    # ---- coffee mug: "WORLD'S BEST BOSS (ME)" -------------------------------
    cv.rounded_rect(62, 598, 80, 58, 10, (240, 240, 235), (40, 40, 50), 3)
    cv.arc(142, 628, 12, 16, 270, 90, (40, 40, 50), 5)
    cv.text("WORLD'S", 68, 606, 1, INK)
    cv.text("BEST BOSS", 68, 622, 1, INK)
    cv.text("(ME)", 68, 638, 1, RED_DK)
    # spilled coffee below the keyboard
    cv.ellipse(172, 717, 42, 11, (90, 55, 20))

    # ---- pen cup -------------------------------------------------------------
    cv.rect(566, 600, 34, 45, (60, 90, 160))
    cv.rect_outline(566, 600, 34, 45, (20, 30, 60), 2)
    cv.line(574, 600, 570, 578, (255, 60, 60), 4)
    cv.line(586, 600, 590, 576, (255, 220, 90), 4)
    cv.line(596, 600, 602, 580, (80, 255, 120), 4)

    # ---- red "FIRED" stamp on the desk ---------------------------------------
    cv.rect_outline(420, 670, 150, 50, RED, 5)
    cv.text("FIRED", 436, 678, 4, RED)

    # ---- top + bottom meme captions -------------------------------------------
    cv.rect(0, 0, W, 160, BLACK)
    y = 12
    for line in TOP_LINES:
        cv.text_centered(line, W // 2, y, 8, WHITE, BLACK, 3)
        y += 68
    cv.rect(0, 800, W, H - 800, BLACK)
    y = 818
    for line in BOTTOM_LINES:
        cv.text_centered(line, W // 2, y, 6, WHITE, BLACK, 3)
        y += 54

    png = encode_png(cv.px, W, H)
    with open(out_path, "wb") as f:
        f.write(png)
    size = len(png)
    assert size <= MAX_BYTES, "%d bytes exceeds 1 MiB" % size
    print("wrote %s (1024x1024, %d bytes)" % (out_path, size))


if __name__ == "__main__":
    sys.exit(main())
