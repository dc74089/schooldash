"""Render an 800x480 PNG for e-paper displays (e.g. Seeed Studio reTerminal E1002).

Draws the daily bell schedule alongside the lunch menu using Pillow. The output
is intentionally high-contrast black-on-white so it renders cleanly on a
monochrome e-ink panel.
"""
import io
import os

from PIL import Image, ImageDraw, ImageFont

WIDTH = 800
HEIGHT = 480
MARGIN = 20

BLACK = 0
WHITE = 255

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "app", "fonts")


def _font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def _fmt_time(t):
    """Format a datetime.time like '8:10' / '12:05' without platform-specific
    strftime directives."""
    hour = t.hour % 12 or 12
    return f"{hour}:{t.minute:02d}"


def _wrap(text, font, max_width):
    """Greedily wrap a string to lines that fit within max_width pixels."""
    words = text.split()
    lines = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if font.getlength(candidate) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def render(schedule_name, bells, lunch, grade, date):
    img = Image.new("L", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    f_date = _font("DejaVuSans-Bold.ttf", 30)
    f_sub = _font("DejaVuSans.ttf", 18)
    f_col_title = _font("DejaVuSans-Bold.ttf", 22)
    f_period = _font("DejaVuSansMono-Bold.ttf", 18)
    f_time = _font("DejaVuSansMono.ttf", 18)
    f_station = _font("DejaVuSans-Bold.ttf", 17)
    f_item = _font("DejaVuSans.ttf", 16)

    # --- Header ---------------------------------------------------------------
    draw.text((MARGIN, MARGIN), date.strftime("%A, %B %-d"), font=f_date, fill=BLACK)
    if schedule_name:
        draw.text((MARGIN, MARGIN + 38), schedule_name, font=f_sub, fill=BLACK)

    header_bottom = 88
    draw.line([(MARGIN, header_bottom), (WIDTH - MARGIN, header_bottom)], fill=BLACK, width=2)

    # --- Column geometry ------------------------------------------------------
    body_top = header_bottom + 14
    col_divider = 320
    left_x = MARGIN
    left_right = col_divider - 20
    right_x = col_divider + 20
    right_right = WIDTH - MARGIN
    right_width = right_right - right_x

    draw.line([(col_divider, header_bottom + 6), (col_divider, HEIGHT - MARGIN)], fill=BLACK, width=1)

    # --- Left column: schedule ------------------------------------------------
    draw.text((left_x, body_top), "Today's Schedule", font=f_col_title, fill=BLACK)
    y = body_top + 34

    if bells:
        row_h = 30
        pad = 5
        # top border of the table
        draw.line([(left_x, y), (left_right, y)], fill=BLACK, width=1)
        for label, start, end in bells:
            text_y = y + pad
            draw.text((left_x + 6, text_y), label, font=f_period, fill=BLACK)
            time_str = f"{_fmt_time(start)} – {_fmt_time(end)}"
            time_w = f_time.getlength(time_str)
            draw.text((left_right - 6 - time_w, text_y), time_str, font=f_time, fill=BLACK)
            y += row_h
            # separator line between this pairing and the next
            draw.line([(left_x, y), (left_right, y)], fill=BLACK, width=1)
    else:
        draw.text((left_x, y), "No school today", font=f_item, fill=BLACK)

    # --- Right column: lunch --------------------------------------------------
    draw.text((right_x, body_top), "Lunch", font=f_col_title, fill=BLACK)
    y = body_top + 34
    bottom_limit = HEIGHT - MARGIN

    if lunch:
        for station, items in lunch.items():
            if y > bottom_limit - 20:
                break
            draw.text((right_x, y), station, font=f_station, fill=BLACK)
            y += 24
            for item in items:
                for line in _wrap(item, f_item, right_width - 16):
                    if y > bottom_limit - 16:
                        break
                    draw.text((right_x + 8, y), f"• {line}", font=f_item, fill=BLACK)
                    y += 20
            y += 6
    else:
        draw.text((right_x, y), "No menu available", font=f_item, fill=BLACK)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
