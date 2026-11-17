"""Tier board states (1080x1920 PNG) in the reference's layout, and the product name cards (transparent PNG).
Rows and colours measured on the reference (Koriderm, 2:22). Product per tier: our choice from the brief."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
D = os.path.dirname(os.path.abspath(__file__))
F = os.path.expanduser('~/.local/share/fonts/')
BOLD = F + 'Montserrat-Bold.ttf'; XB = F + 'Montserrat-ExtraBold.ttf'
ROWS = [('S', 'Best value', '#ee3c3c', 14, 386), ('A', 'Worth it', '#fb9a14', 406, 780), ('B', 'Decent', '#56ab31', 800, 1175),
        ('C', 'Average', '#3b8cef', 1195, 1570), ('D', 'Overpriced', '#a5a5a5', 1590, 1898)]
X0, TILE, X1, R = 22, 208, 1060, 18
# 2026-11-14 (user: she and the caption covered the C-tier products): packed into the row's left half as the inspo
# does (its items sit at x ~240-660, about 0.6 of the row tall, touching), so her cutout at the right never covers one.
# The Aveli probe stands upright like the inspo's microneedling pen. Old layout in edit/backup-2026-11-14-board-pack/.
# 2026-11-15 (client Loom 4): home-device.png is the device alone, the gel tube cut off (original: home-device-with-gel.png).
# 2026-11-14 (user: "so close ... leave some space, increase the size; fine if the caption shows a bit"): bigger items,
# real gaps, C row centred in its row again (caption may overlap a little).
ITEM_H, ITEM_W, GAP = 0.70, 150, 26
# C row: 4 items, her cutout's shoulder takes the row's lower right (edge about x 820 at the row top, 630 at the bottom),
# so they stand at the top of the row from x 236, the caption crossing them a little (user OK).
C_H, C_X, C_TOP = 0.62, 236, 22
# 2026-11-14 (user: the caption sat on the C-tier products): the caption box (centre y 1367, 80 tall: y 1327-1407) crosses
# the C row, so C items stand in the band under it (y 1415-1562), bottoms on one line, never behind the caption.
CAP_Y1 = (1415, 1562)
WIDE = {'cellulite-cream': 250}
def item(name, h):
    im = Image.open(f'{D}/{name}.png')
    if im.width > 2.5 * im.height:
        im = im.rotate(90, expand=True)
    s = h / im.height
    cap = WIDE.get(name, ITEM_W)  # a squat jar may run wider (it sits alone in D)
    if im.width * s > cap: s = cap / im.width
    return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
def layout(content):
    """(name, image, (x, y)) for every product on a board with this content."""
    out = []
    for L, lab, col, y0, y1 in ROWS:
        cy = (y0 + y1) / 2
        x = C_X if L == 'C' else 250
        for n in content.get(L, []):
            if L == 'C':
                it = item(n, (y1 - y0) * C_H); out.append((n, it, (x, y0 + C_TOP)))
            else:
                it = item(n, (y1 - y0) * ITEM_H); out.append((n, it, (x, round(cy - it.height / 2))))
            x += it.width + GAP
    return out
def board(content):
    W, H = 1080, 1920
    img = Image.new('RGB', (W, H), '#f6f6f6'); d = ImageDraw.Draw(img)
    for L, lab, col, y0, y1 in ROWS:
        d.rounded_rectangle((X0, y0, X1, y1), R, fill='white', outline='#e3e3e3', width=2)
        d.rounded_rectangle((X0, y0, TILE, y1), R, fill=col); d.rectangle((TILE - R, y0, TILE, y1), fill=col)
        cy = (y0 + y1) / 2
        d.text(((X0 + TILE) / 2, cy - 18), L, font=ImageFont.truetype(BOLD, 64), fill='white', anchor='ms')
        d.text(((X0 + TILE) / 2, cy + 32), lab, font=ImageFont.truetype(BOLD, 26), fill='white', anchor='ms')
    for n, it, xy in layout(content):
        img.paste(it, xy, it)
    return img
def items_layer(content, names):
    """Transparent 1080x1920 layer with only these products, where they sit on the board (they slide in)."""
    lay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    for n, it, xy in layout(content):
        if n in names: lay.alpha_composite(it, xy)
    return lay
STATES = {'D': {'D': ['cellulite-cream']}}
STATES['C1'] = dict(STATES['D'], C=['dry-brush'])
STATES['C2'] = dict(STATES['D'], C=['dry-brush', 'aveli-probe'])
STATES['C3'] = dict(STATES['D'], C=['dry-brush', 'aveli-probe', 'cellulite-leggings'])
STATES['C4'] = dict(STATES['D'], C=['dry-brush', 'aveli-probe', 'cellulite-leggings', 'home-device'])
STATES['B'] = dict(STATES['C4'], B=['cellulite-oil'])
STATES['S'] = dict(STATES['B'], S=['aleo-bottle'])
STATES['empty'] = {}
for k, c in STATES.items():
    board(c).save(f'{D}/board-{k}.png')
# 2026-11-15 (client Loom 4: the board stays put, only the product being ranked swooshes in from the right):
# item-<state>.png = that state's new product alone, at its board position; the board under it is the state before.
PREV = {'D': 'empty', 'C1': 'D', 'C2': 'C1', 'C3': 'C2', 'C4': 'C3', 'B': 'C4', 'S': 'B'}
for k, p in PREV.items():
    new = [n for L, ns in STATES[k].items() for n in ns if n not in STATES[p].get(L, [])]
    items_layer(STATES[k], new).save(f'{D}/item-{k}.png')
# name cards: white ALL CAPS Montserrat ExtraBold, thin white bar at left, soft shadow, lower left (reference); ends at y 1300, above our captions (ours: the reference hides the caption under its card)
CARDS = {'creams': 'CELLULITE\nCREAMS', 'dry-brushing': 'DRY\nBRUSHING', 'aveli': 'AVELI', 'leggings': 'CELLULITE\nLEGGINGS',
         'devices': 'AT-HOME\nDEVICES', 'oils': 'CELLULITE\nOILS'}
f = ImageFont.truetype(XB, 74); PITCH = 84
for k, t in CARDS.items():
    lines = t.split('\n'); n = len(lines)
    lay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # text centred on the bar (user 2026-11-14): caps block from the first cap top to the last baseline, PAD each side
    capH = -f.getbbox('H', anchor='ls')[1]; PAD = 10
    base = [1300 - PAD - (n - 1 - i) * PITCH for i in range(n)]
    d.rectangle((104, base[0] - capH - PAD, 111, 1300), fill='white')
    for i, ln in enumerate(lines):
        d.text((132, base[i]), ln, font=f, fill='white', anchor='ls')
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel('A').point(lambda v: int(v * 0.55)))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    out = Image.new('RGBA', lay.size, (0, 0, 0, 0)); out.alpha_composite(sh, (0, 3)); out.alpha_composite(lay)
    out.save(f'{D}/card-{k}.png')
print('ok')
# 6-frame slide-in clips (24 fps): the board before, the new product easing in from the right (x +1080 -> 0,
# ease-out cubic), last frame settled. They sit on V2 under her cutout (edit/board_items.py).
import subprocess, tempfile
N = 6
for k, p in PREV.items():
    base = Image.open(f'{D}/board-{p}.png').convert('RGBA'); lay = Image.open(f'{D}/item-{k}.png')
    with tempfile.TemporaryDirectory() as td:
        for i in range(N):
            u = 1 - (1 - (i + 1) / N) ** 3
            fr = base.copy(); fr.alpha_composite(lay, (round(1080 * (1 - u)), 0)) if u < 1 else fr.alpha_composite(lay)
            fr.convert('RGB').save(f'{td}/f{i:02d}.png')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', f'{td}/f%02d.png', '-c:v', 'libx264',
                        '-crf', '10', '-vf', 'scale=out_color_matrix=bt709:out_range=tv', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-r', '24', f'{D}/slide-{k}.mp4'], check=True)
print('slides ok')
