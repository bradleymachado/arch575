# PinUp_QR_v1.1 - minimal QR encoder (byte mode, version 3, ECC level M), after Nayuki's reference implementation.
# This section is intended to encode a URL (<= 42 bytes) without a QR library (none installable here), verify it
# decodes with OpenCV, and write a PNG and, if OUT ends in .svg, a crisp SVG for the web deck (v1.1, 2026-10-09).
# Usage: python PinUp_QR_v1.1.py <text> <out.png|out.svg> [fg_hex] [bg_hex]
import sys
import numpy as np
from PIL import Image

TEXT = sys.argv[1]; OUT = sys.argv[2]
FG = sys.argv[3] if len(sys.argv) > 3 else '241E4E'
BG = sys.argv[4] if len(sys.argv) > 4 else 'FDFFFC'
hx = lambda h: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
VER, SIZE = 3, 29
DATA_CW, ECC_CW = 44, 26          # version 3-M: one block, 44 data + 26 ECC codewords
ECL_BITS = 0                       # M = 00

# ---- data codewords
bits = []
def put(v, n):
    for i in range(n - 1, -1, -1): bits.append((v >> i) & 1)
data = TEXT.encode("utf-8")
assert len(data) <= 42
put(0b0100, 4); put(len(data), 8)
for b in data: put(b, 8)
cap = DATA_CW * 8
put(0, min(4, cap - len(bits)))
while len(bits) % 8: bits.append(0)
pad = [0xEC, 0x11]; k = 0
while len(bits) < cap: put(pad[k % 2], 8); k += 1
dcw = [int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, cap, 8)]

# ---- Reed-Solomon over GF(256), poly 0x11D
def gmul(x, y):
    z = 0
    for i in range(7, -1, -1):
        z = (z << 1) ^ ((z >> 7) * 0x11D)
        z ^= ((y >> i) & 1) * x
    return z & 0xFF
def rs_divisor(deg):
    res = [0] * (deg - 1) + [1]; root = 1
    for _ in range(deg):
        for j in range(deg):
            res[j] = gmul(res[j], root)
            if j + 1 < deg: res[j] ^= res[j + 1]
        root = gmul(root, 0x02)
    return res
def rs_rem(data, div):
    res = [0] * len(div)
    for b in data:
        f = b ^ res.pop(0); res.append(0)
        for i, c in enumerate(div): res[i] ^= gmul(c, f)
    return res
ecw = rs_rem(dcw, rs_divisor(ECC_CW))
allcw = dcw + ecw

# ---- function patterns
M = np.zeros((SIZE, SIZE), int); F = np.zeros((SIZE, SIZE), bool)
def setf(x, y, d): M[y, x] = 1 if d else 0; F[y, x] = True
for i in range(SIZE):
    setf(6, i, i % 2 == 0); setf(i, 6, i % 2 == 0)
def finder(cx, cy):
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            d = max(abs(dx), abs(dy)); x, y = cx + dx, cy + dy
            if 0 <= x < SIZE and 0 <= y < SIZE: setf(x, y, d not in (2, 4))
finder(3, 3); finder(SIZE - 4, 3); finder(3, SIZE - 4)
def align(cx, cy):
    for dy in range(-2, 3):
        for dx in range(-2, 3): setf(cx + dx, cy + dy, max(abs(dx), abs(dy)) != 1)
align(22, 22)
def draw_format(mask):
    data = ECL_BITS << 3 | mask
    rem = data
    for _ in range(10): rem = (rem << 1) ^ ((rem >> 9) * 0x537)
    b = (data << 10 | rem) ^ 0x5412
    g = lambda i: (b >> i) & 1
    for i in range(0, 6): setf(8, i, g(i))
    setf(8, 7, g(6)); setf(8, 8, g(7)); setf(7, 8, g(8))
    for i in range(9, 15): setf(14 - i, 8, g(i))
    for i in range(0, 8): setf(SIZE - 1 - i, 8, g(i))
    for i in range(8, 15): setf(8, SIZE - 15 + i, g(i))
    setf(8, SIZE - 8, 1)
draw_format(0)  # reserve

# ---- codeword placement
cwbits = []
for c in allcw:
    for i in range(7, -1, -1): cwbits.append((c >> i) & 1)
i = 0; right = SIZE - 1
while right >= 1:
    if right == 6: right = 5
    for vert in range(SIZE):
        for j in range(2):
            x = right - j; upward = ((right + 1) & 2) == 0
            y = SIZE - 1 - vert if upward else vert
            if not F[y, x] and i < len(cwbits):
                M[y, x] = cwbits[i]; i += 1
    right -= 2
base = M.copy()

MASKS = [lambda x, y: (x + y) % 2 == 0, lambda x, y: y % 2 == 0, lambda x, y: x % 3 == 0, lambda x, y: (x + y) % 3 == 0,
         lambda x, y: (x // 3 + y // 2) % 2 == 0, lambda x, y: x * y % 2 + x * y % 3 == 0,
         lambda x, y: (x * y % 2 + x * y % 3) % 2 == 0, lambda x, y: ((x + y) % 2 + x * y % 3) % 2 == 0]
def penalty(m):
    p = 0
    for arr in (m, m.T):
        for row in arr:
            run = 1
            for a, b in zip(row[:-1], row[1:]):
                if a == b: run += 1
                else:
                    if run >= 5: p += run - 2
                    run = 1
            if run >= 5: p += run - 2
    p += 3 * sum(1 for y in range(SIZE - 1) for x in range(SIZE - 1) if m[y, x] == m[y, x + 1] == m[y + 1, x] == m[y + 1, x + 1])
    dark = m.sum() / m.size; p += int(abs(dark * 20 - 10)) * 10
    return p

def build(mask):
    global M
    M = base.copy()
    for y in range(SIZE):
        for x in range(SIZE):
            if not F[y, x] and MASKS[mask](x, y): M[y, x] ^= 1
    draw_format(mask)
    return M.copy()

def render(m, scale=40, quiet=4, fg=None, bg=None):
    fg = fg or hx(FG); bg = bg or hx(BG)
    n = SIZE + 2 * quiet
    img = np.zeros((n, n, 3), np.uint8); img[:] = bg
    img[quiet:quiet + SIZE, quiet:quiet + SIZE][m == 1] = fg
    return Image.fromarray(img).resize((n * scale, n * scale), Image.NEAREST)

import cv2
det = cv2.QRCodeDetector()
cands = sorted(range(8), key=lambda k: penalty(build(k)))
for k in cands:
    m = build(k); im = render(m)
    txt, pts, _ = det.detectAndDecode(cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR))
    print("mask", k, "penalty", penalty(m), "decoded:", repr(txt))
    if txt == TEXT:
        if OUT.lower().endswith('.svg'):
            q = 4; n = SIZE + 2 * q
            d = ''.join('M%d %dh1v1h-1z' % (x + q, y + q) for y in range(SIZE) for x in range(SIZE) if m[y, x])
            svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" shape-rendering="crispEdges">'
                   '<rect width="%d" height="%d" fill="#%s"/><path fill="#%s" d="%s"/></svg>\n') % (n, n, n, n, BG, FG, d)
            open(OUT, 'w', encoding='ascii').write(svg)
            im.save(OUT[:-4] + '.png')
            print("saved", OUT, "and", OUT[:-4] + '.png', im.size)
        else:
            im.save(OUT); print("saved", OUT, im.size)
        break
else:
    raise SystemExit("no mask decoded")
