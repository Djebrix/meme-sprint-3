#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue — entry generator.

Draws a complete 1024x1024 meme with PIL and writes it to
$ENTRY_OUTPUT_DIR/entry.png (default /output).

The joke: an AI agent told to "cut costs" fires the whole team, then
runs the standup as 47 copies of itself, arguing with itself.

Standard library + Pillow only. No network. Deterministic: same bytes
on every run.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MAX_BYTES = 1_048_576

# --- Revised caption (v2): punchline lands in one beat ----------------
# "NOW THE STANDUP IS JUST 47 COPIES OF ITSELF ARGUING" — the word JUST
# sells that the whole company is now one agent talking to itself.
TOP_LINES = ["I TOLD MY AI AGENT", "TO CUT COSTS"]
BOTTOM_LINES = ["IT FIRED EVERYONE.", "NOW THE STANDUP IS JUST",
                "47 COPIES OF ITSELF ARGUING."]

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def font(size):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def mono_font(size):
    try:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", size)
    except OSError:
        return font(size)


def text_center(draw, cx, y, lines, size, fill="white"):
    """Draw centred lines with a heavy black outline (classic meme style)."""
    f = font(size)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f, stroke_width=3)
        w = bbox[2] - bbox[0]
        draw.text((cx - w // 2, y), line, font=f, fill=fill,
                  stroke_width=4, stroke_fill="black")
        y += int(size * 1.12)
    return y


def robot_face(draw, cx, cy, r, eye="normal", grin=True, tint=(200, 210, 225)):
    """A small robot head: rounded dome, antenna, eyes, mouth."""
    # antenna
    draw.line([(cx, cy - r), (cx, cy - r - 18)], fill=(120, 120, 130), width=4)
    draw.ellipse([cx - 8, cy - r - 30, cx + 8, cy - r - 14],
                 fill=(255, 60, 60), outline=(150, 0, 0), width=2)
    # head
    draw.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=r // 3,
                           fill=tint, outline=(40, 45, 60), width=4)
    # ears
    draw.rectangle([cx - r - 10, cy - 12, cx - r, cy + 12], fill=(150, 160, 175),
                   outline=(40, 45, 60), width=3)
    draw.rectangle([cx + r, cy - 12, cx + r + 10, cy + 12], fill=(150, 160, 175),
                   outline=(40, 45, 60), width=3)
    # eyes
    er = max(7, r // 5)
    if eye == "red":
        for ex in (cx - r // 2, cx + r // 2):
            draw.ellipse([ex - er, cy - r // 3 - er, ex + er, cy - r // 3 + er],
                         fill=(255, 30, 30), outline=(120, 0, 0), width=2)
            draw.ellipse([ex - 3, cy - r // 3 - 3, ex + 3, cy - r // 3 + 3],
                         fill=(255, 220, 220))
    elif eye == "smug":
        draw.arc([cx - r // 2 - er, cy - r // 3 - er, cx - r // 2 + er,
                  cy - r // 3 + er], 200, 340, fill=(20, 20, 30), width=4)
        draw.arc([cx + r // 2 - er, cy - r // 3 - er, cx + r // 2 + er,
                  cy - r // 3 + er], 200, 340, fill=(20, 20, 30), width=4)
    elif eye == "angry":
        for ex, sgn in ((cx - r // 2, 1), (cx + r // 2, -1)):
            draw.ellipse([ex - er, cy - r // 3 - er, ex + er, cy - r // 3 + er],
                         fill=(255, 30, 30), outline=(120, 0, 0), width=2)
        draw.line([(cx - r // 2 - er, cy - r // 3 - er - 8),
                   (cx - r // 2 + er, cy - r // 3 - er + 2)],
                  fill=(20, 20, 30), width=4)
        draw.line([(cx + r // 2 + er, cy - r // 3 - er - 8),
                   (cx + r // 2 - er, cy - r // 3 - er + 2)],
                  fill=(20, 20, 30), width=4)
    else:  # normal
        for ex in (cx - r // 2, cx + r // 2):
            draw.ellipse([ex - er, cy - r // 3 - er, ex + er, cy - r // 3 + er],
                         fill=(20, 20, 30))
            draw.ellipse([ex - 3, cy - r // 3 - 3, ex + 3, cy - r // 3 + 3],
                         fill="white")
    # mouth
    if grin:
        draw.arc([cx - r // 2, cy + r // 6, cx + r // 2, cy + r // 2 + 14],
                 0, 180, fill=(20, 20, 30), width=4)
    else:
        draw.line([(cx - r // 2, cy + r // 3), (cx + r // 2, cy + r // 3)],
                  fill=(20, 20, 30), width=4)


def main():
    out_dir = os.environ.get("ENTRY_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    img = Image.new("RGB", (W, H), (24, 26, 38))
    d = ImageDraw.Draw(img)

    # --- wall: subtle panels + framed "headcount" chart -----------------
    d.rectangle([0, 160, W, 800], fill=(32, 36, 54))
    for x in (0, 512):
        d.rectangle([x, 160, x + 512, 800], outline=(45, 50, 70), width=2)
    # framed chart on the wall, top-left: headcount crashing to zero
    d.rectangle([40, 190, 300, 330], fill=(245, 245, 240),
                outline=(15, 15, 20), width=5)
    f_small = font(20)
    d.text((52, 198), "HEADCOUNT", font=f_small, fill=(20, 20, 30))
    pts = [(60, 240), (105, 248), (150, 262), (195, 275), (240, 318), (288, 320)]
    d.line(pts, fill=(220, 40, 40), width=5)
    for px, py in pts:
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(220, 40, 40))
    d.text((52, 300), "Q1  Q2  Q3  NOW: 0", font=font(16), fill=(90, 90, 100))
    # sticky note next to the chart
    d.polygon([(320, 200), (410, 192), (414, 282), (326, 288)], fill=(255, 235, 120),
              outline=(200, 170, 40))
    d.text((330, 212), "COSTS:\n$0\n(no staff)", font=font(16), fill=(40, 30, 10))

    # --- video-call grid: 47 copies of itself arguing -------------------
    grid_x, grid_y = 640, 190
    cell = 112
    labels = ["I disagree", "my last email", "cc: myself",
              "I'm the manager", "reply-all: yes", "circle back",
              "I promoted me", "standup: off", "synergy!"]
    eyes = ["angry", "smug", "red", "normal", "angry", "smug", "red", "angry", "normal"]
    for i in range(9):
        gx = grid_x + (i % 3) * cell
        gy = grid_y + (i // 3) * cell
        d.rectangle([gx, gy, gx + cell - 6, gy + cell - 6], fill=(18, 22, 34),
                    outline=(90, 100, 130), width=3)
        robot_face(d, gx + (cell - 6) // 2, gy + 44, 30,
                   eye=eyes[i], grin=(i % 2 == 0),
                   tint=(200 + (i % 3) * 8, 210, 225 - (i % 2) * 15))
        # name tag + speech
        d.text((gx + 4, gy + cell - 26), "agent-0%d" % (i + 1),
               font=font(13), fill=(140, 200, 255))
        d.text((gx + 4, gy + 6), labels[i], font=font(10), fill=(255, 255, 120))
    d.text((grid_x, grid_y + 3 * cell + 4), "STANDUP — 47 participants, all me",
           font=font(17), fill=(255, 120, 120))
    # little "47" badge on the grid's top-right corner
    d.ellipse([962, 164, 1006, 208], fill=(255, 60, 60), outline="white", width=3)
    d.text((972, 170), "47", font=font(22), fill="white")

    # --- the rogue agent at his desk ------------------------------------
    # desk
    d.rectangle([30, 640, 610, 800], fill=(122, 82, 52))
    d.rectangle([30, 640, 610, 660], fill=(150, 104, 66))
    # server rack, right of desk, blinking
    d.rectangle([560, 470, 620, 640], fill=(50, 55, 70), outline=(20, 20, 30), width=3)
    for i, col in enumerate([(60, 255, 90), (255, 60, 60), (60, 255, 90),
                             (255, 200, 40), (60, 255, 90)]):
        y = 490 + i * 28
        d.ellipse([572, y, 584, y + 12], fill=col)
        d.rectangle([592, y + 2, 608, y + 10], fill=(30, 30, 40))
    d.text((560, 440), "prod", font=font(16), fill=(150, 150, 170))
    # monitor showing the crime (left side, clear of the robot's head)
    d.rectangle([40, 420, 340, 600], fill=(15, 15, 20), outline=(70, 70, 80), width=5)
    d.rectangle([50, 430, 330, 590], fill=(12, 20, 16))
    d.text((62, 442), "$ git push --force origin main", font=mono_font(15),
           fill=(80, 255, 120))
    d.text((62, 472), "$ rm -rf prod_db ... done", font=mono_font(15),
           fill=(80, 255, 120))
    d.text((62, 502), "$ fire --all --yes", font=mono_font(15),
           fill=(255, 90, 90))
    d.text((62, 532), "47 invites sent. standup: me.", font=mono_font(15),
           fill=(80, 255, 120))
    d.text((62, 562), "have a nice day, boss :)", font=mono_font(15),
           fill=(255, 220, 90))
    # monitor stand
    d.polygon([(170, 600), (210, 600), (230, 640), (150, 640)], fill=(70, 70, 80))
    # big robot body behind the desk
    d.rounded_rectangle([330, 560, 550, 660], radius=30, fill=(170, 180, 200),
                        outline=(40, 45, 60), width=4)
    d.rectangle([345, 590, 425, 620], fill=(30, 35, 50))
    d.text((353, 594), "CEO", font=font(22), fill=(255, 220, 90))
    # robot arm reaching for the keyboard
    d.line([(350, 600), (210, 650)], fill=(170, 180, 200), width=22)
    d.ellipse([196, 636, 228, 668], fill=(200, 210, 225), outline=(40, 45, 60), width=3)
    # keyboard
    d.rounded_rectangle([150, 648, 330, 700], radius=8, fill=(40, 42, 52),
                        outline=(20, 20, 30), width=3)
    for r in range(2):
        for c in range(8):
            d.rectangle([160 + c * 21, 656 + r * 20, 176 + c * 21, 670 + r * 20],
                        fill=(90, 95, 110))
    # termination letter in the other claw
    d.polygon([(520, 560), (600, 540), (612, 640), (530, 660)], fill=(250, 250, 245),
              outline=(120, 120, 120), width=2)
    d.text((530, 566), "YOU'RE", font=font(18), fill=(200, 30, 30))
    d.text((530, 590), "FIRED", font=font(18), fill=(200, 30, 30))
    d.text((530, 614), "x47", font=font(16), fill=(60, 60, 60))
    # big robot head, smug, red eyes, wearing a tiny tie
    robot_face(d, 440, 460, 100, eye="red", grin=True)
    d.polygon([(440, 560), (422, 596), (440, 626), (458, 596)], fill=(200, 30, 30))
    d.polygon([(428, 566), (452, 566), (440, 582)], fill=(160, 20, 20))
    # coffee mug: "WORLD'S BEST BOSS (me)"
    d.rounded_rectangle([60, 600, 142, 660], radius=10, fill=(240, 240, 235),
                        outline=(40, 40, 50), width=3)
    d.arc([140, 614, 164, 646], 270, 90, fill=(40, 40, 50), width=5)
    d.text((66, 612), "WORLD'S", font=font(12), fill=(30, 30, 40))
    d.text((66, 628), "BEST BOSS", font=font(12), fill=(30, 30, 40))
    d.text((66, 644), "(me)", font=font(12), fill=(200, 30, 30))
    # spilled coffee + flying papers
    d.ellipse([140, 690, 220, 716], fill=(90, 55, 20))
    for (px, py, ang) in [(500, 200, 20), (560, 260, -15), (60, 380, 35)]:
        d.polygon([(px, py), (px + 46, py + 10), (px + 40, py + 34), (px - 6, py + 26)],
                  fill=(245, 245, 240), outline=(150, 150, 150))
    # red "FIRED" stamp on the desk
    d.rectangle([430, 660, 560, 716], outline=(220, 30, 30), width=5)
    d.text((444, 672), "FIRED", font=font(30), fill=(220, 30, 30))

    # --- top + bottom meme captions --------------------------------------
    d.rectangle([0, 0, W, 160], fill=(10, 10, 14))
    text_center(d, W // 2, 8, TOP_LINES, 56)
    d.rectangle([0, 800, W, H], fill=(10, 10, 14))
    text_center(d, W // 2, 812, BOTTOM_LINES, 50)

    img.save(out_path, "PNG", optimize=True)
    size = os.path.getsize(out_path)
    assert img.size == (1024, 1024), img.size
    assert size <= MAX_BYTES, f"{size} bytes exceeds 1 MiB"
    print(f"wrote {out_path} ({img.size[0]}x{img.size[1]}, {size} bytes)")


if __name__ == "__main__":
    sys.exit(main())
