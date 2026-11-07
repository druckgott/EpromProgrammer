# Lochraster-Shield (README 4.8): Mega-Stiftleiste in der Mitte, Sockelleisten links/rechts, je Reihe eine gerade Loetbahn.
# Koordinaten (Spalte, Reihe) = Aufdruck der Platine, Ansicht LOETSEITE. Prueft Netze (jedes Loch ein Netz, jedes Netz verbunden).
# Aufruf: python -X utf8 tools/lochraster_shield.py images/lochraster_shield.svg  -> SVG (Ansicht von oben), Markdown-Tabellen (stdout), C-Pinlisten fuer defines.h (stderr)
import sys

ODD_COL, EVEN_COL = 19, 20            # Annahme: gerade Mega-Pins = innere Reihe (zur Mega-Mitte)
SL, SR = 17, 23                       # Sockelleisten (6 Loecher = 15,24 mm)
def hdr(n):
    if n == '5V':  return [(ODD_COL, 8), (EVEN_COL, 8)]
    if n == 'GND': return [(ODD_COL, 25), (EVEN_COL, 25)]
    return (EVEN_COL if n % 2 == 0 else ODD_COL, 9 + (n - 22) // 2)
def sock(p):                          # Loetseite: Pin 1..16 rechts, 17..32 links, Pin 1/32 oben (Reihe 9)
    return (SR, 8 + p) if p <= 16 else (SL, 41 - p)

LABEL = {1:'VPP',2:'A16',3:'A15',4:'A12',5:'A7',6:'A6',7:'A5',8:'A4',9:'A3',10:'A2',11:'A1',12:'A0',
         13:'Q0',14:'Q1',15:'Q2',16:'VSS',17:'Q3',18:'Q4',19:'Q5',20:'Q6',21:'Q7',22:'E',23:'A10',
         24:'G',25:'A11',26:'A9',27:'A8',28:'A13',29:'A14',30:'A17',31:'A18',32:'VCC'}
# Neue Zuordnung ergibt sich aus der Geometrie: EPROM-Pin <-> Mega-Pin in derselben Reihe
MEGA = {}
for p in range(1, 33):
    if p in (1, 32, 16): continue
    c, r = sock(p)
    n = 22 + 2 * (r - 9) + (0 if c == SR else 1)
    MEGA[p] = n
VPP_EN, VCC_EN, SPARE = 22, 23, 52
assert set(MEGA.values()) | {VPP_EN, VCC_EN, SPARE} == set(range(22, 54))

PARTS = {
 'J1':        {'+6,25 V':(19,1), 'GND':(20,1), '+12,75 V':(21,1)},
 'Q1 BC337':  {'E':(20,2), 'B':(21,2), 'C':(22,2)},
 'R1 1k':     {'b':(21,3), 'a':(21,4)},
 'R2 1k':     {'a':(22,3), 'b':(22,4)},
 'Q2 BC327':  {'E':(23,3), 'B':(23,4), 'C':(23,5)},
 'R3 10k':    {'a':(24,3), 'b':(24,4)},
 'D2 1N5819': {'A':(17,6), 'K':(23,6)},
 'D1 1N5819': {'K':(18,7), 'A':(19,7)},
 'Q4 S8550':  {'E':(17,3), 'B':(17,4), 'C':(17,5)},
 'R6 10k':    {'a':(16,3), 'b':(16,4)},
 'R5 1k':     {'a':(15,4), 'b':(15,5)},
 'Q3 S8050':  {'C':(15,6), 'B':(15,7), 'E':(15,8)},
 'R4 1k':     {'a':(14,7), 'b':(14,8)},
}
P = lambda part, leg: PARTS[part][leg]
NETLEGS = {   # Netz -> Pflicht-Anschluesse
 'GND':    hdr('GND') + [sock(16), P('Q1 BC337','E'), P('Q3 S8050','E'), P('J1','GND')],
 '5V':     [hdr('5V')[1], P('D1 1N5819','A')],
 'VCC':    [sock(32), P('D2 1N5819','A'), P('D1 1N5819','K'), P('Q4 S8550','C')],
 'VPP':    [sock(1), P('D2 1N5819','K'), P('Q2 BC327','C')],
 'VPP_EN': [hdr(VPP_EN), P('R1 1k','a')],
 'B1':     [P('R1 1k','b'), P('Q1 BC337','B')],
 'C1':     [P('Q1 BC337','C'), P('R2 1k','a')],
 'B2':     [P('R2 1k','b'), P('Q2 BC327','B'), P('R3 10k','b')],
 '+12V75': [P('J1','+12,75 V'), P('Q2 BC327','E'), P('R3 10k','a')],
 'VCC_EN': [hdr(VCC_EN), P('R4 1k','b')],
 'B3':     [P('R4 1k','a'), P('Q3 S8050','B')],
 'C3':     [P('Q3 S8050','C'), P('R5 1k','b')],
 'B4':     [P('R5 1k','a'), P('Q4 S8550','B'), P('R6 10k','b')],
 '+6V25':  [P('J1','+6,25 V'), P('Q4 S8550','E'), P('R6 10k','a')],
}
for p, n in MEGA.items(): NETLEGS[LABEL[p]] = [sock(p), hdr(n)]

# Loetbahnen (auf der Loetseite, Loch an Loch) je Netz
TR = {
 'GND':    [[sock(16), (23,25), (22,25), (21,25)], [(18,25), (17,25), (16,25)] + [(16, r) for r in range(24, 6, -1)],
            [(16,8), (15,8)], [(19,2), (20,2), (20,1)]],
 '5V':     [[(20,7), (19,7)]],
 'VCC':    [[(17,9), (17,8), (17,7), (17,6), (17,5)], [(18,7), (17,7)]],
 'VPP':    [[(23,9), (23,8), (23,7), (23,6), (23,5)]],
 'VPP_EN': [[(21,9), (21,8), (21,7), (21,6), (21,5), (21,4)]],
 'B1':     [[(21,3), (21,2)]],
 'C1':     [[(22,2), (22,3)]],
 'B2':     [[(22,4), (23,4), (24,4)]],
 '+12V75': [[(21,1), (22,1), (23,1), (23,2), (23,3), (24,3)]],
 'VCC_EN': [[(18,9), (18,8)], [(13,8), (14,8)]],
 'B3':     [[(14,7), (15,7)]],
 'C3':     [[(15,6), (15,5)]],
 'B4':     [[(15,4), (16,4), (17,4)]],
 '+6V25':  [[(19,1), (18,1), (17,1), (17,2), (17,3), (16,3)]],
}
for p, n in MEGA.items():
    (c, r), (hc, _) = sock(p), hdr(n)
    step = 1 if hc > c else -1
    TR[LABEL[p]] = [[(x, r) for x in range(c, hc, step)]]          # endet im Loch neben dem Mega-Stift
# Z-Draehte: Mega-Stiftleiste mit Kunststoff UNTER der Platine, die kurzen Stiftenden ragen oben heraus.
# Die Pads der Stifte sind vom Kunststoff verdeckt -> Draht oben am Stiftende anloeten, durchs Nachbarloch
# nach unten, unten als Bahn weiter. (Stift-Loch, Nachbarloch, Netz)
ZW = [(hdr(n), (hdr(n)[0] + (-1 if hdr(n)[0] == ODD_COL else 1), hdr(n)[1]), LABEL[p]) for p, n in MEGA.items()]
ZW += [(hdr(VCC_EN), (18,9), 'VCC_EN'), (hdr(VPP_EN), (21,9), 'VPP_EN'), ((20,8), (20,7), '5V'),
       ((19,25), (18,25), 'GND'), ((20,25), (21,25), 'GND'), ((19,25), (20,25), 'GND')]   # GND: ein Buegel ueber beide Stifte
KEEPOUT = {(c, r) for c in (ODD_COL, EVEN_COL) for r in range(8, 26)}   # unten vom Kunststoff verdeckt
# Isolierte Drahtbruecken (Bauteilseite)
WIRES = [((19,2), (16,7), 'GND'), ((18,8), (13,8), 'VCC_EN')]   # Draht nicht ins Loch eines Bauteilbeins

# ---------- Pruefung: jedes Loch genau ein Netz, jedes Netz zusammenhaengend ----------
hole = {}
def take(h, net):
    assert 1 < h[0] <= 26 and 1 <= h[1] <= 32, ('ausserhalb', h)
    assert hole.get(h, net) == net, ('Kurzschluss', h, hole[h], net)
    hole[h] = net
for net, legs in NETLEGS.items():
    for h in legs: take(h, net)
for name, legs in PARTS.items():
    for h in legs.values(): assert h in hole, ('Bein ohne Netz', name, h)
for net, paths in TR.items():
    for path in paths:
        for a, b in zip(path, path[1:]): assert abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1, ('nicht benachbart', net, a, b)
        for h in path: take(h, net)
for a, b, net in WIRES + ZW: take(a, net); take(b, net)
assert not KEEPOUT & {h for paths in TR.values() for p in paths for h in p}, 'Bahn unter dem Stiftleisten-Kunststoff'
used_by_part_or_sock = {h for legs in PARTS.values() for h in legs.values()} | {sock(p) for p in range(1, 33)}
parent = {}
def f(x):
    parent.setdefault(x, x)
    while parent[x] != x: x = parent[x]
    return x
for paths in TR.values():
    for path in paths:
        for a, b in zip(path, path[1:]): parent[f(a)] = f(b)
for a, b, _ in WIRES + ZW: parent[f(a)] = f(b)
for net, legs in NETLEGS.items():
    roots = {f(h) for h in legs}
    assert len(roots) == 1, ('Netz nicht verbunden', net, legs)
assert hdr(SPARE) not in hole, 'Ersatz-Pin belegt'
print('OK: Netze geprueft', file=sys.stderr)

# ---------- SVG: zwei Ansichten, Mega halbdurchsichtig dahinter ----------
# Mega-Umriss in Platinen-Koordinaten, GESCHAETZT aus der Pinout-Grafik (lastminuteengineers), nicht nachgemessen:
# Kante ca. 1 Raster neben der ungeraden Reihe, 1,2 Raster ueber 5V, 3 Raster unter GND hinaus;
# Buchsenleiste D21..D14 auf Hoehe der 5V-Reihe ab ca. Spalte 22,7, A15..A8 ca. Reihe 27,2 ab Spalte 20,75.
MEGA_EDGE = (18.0, 6.8, 28.0)          # Kante (Spalte), oben (Reihe), unten (Reihe)
DIG = [(22.7 + k, 8.0, f'D{21-k}') for k in range(8)]
ANA = [(20.75 + k, 27.25, f'A{15-k}') for k in range(8)]
TO92 = {'Q1 BC337':'CBE', 'Q2 BC327':'CBE', 'Q3 S8050':'EBC', 'Q4 S8550':'EBC'}   # flache Seite zu dir, links->rechts
S, OX, OY, NC = 28, 170, 170, 31        # NC: gezeichnete Spalten (Platine 1..26, dahinter Mega bis 31)

def svg(path, solder):
    X = (lambda c: OX + (c - 1) * S) if solder else (lambda c: OX + (NC - c) * S)
    Y = lambda r: OY + (r - 1) * S
    out = (lambda c: 1 if X(c) > X(20) else -1)        # Richtung "weg von der Mitte"
    o = []; w = o.append
    W, H = OX + (NC - 1) * S + 360, OY + 33 * S + 20
    w(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Segoe UI, Helvetica, Arial, sans-serif">')
    w(f'<rect width="{W}" height="{H}" fill="#fff"/>')
    if solder:
        head = ['Lochraster-Shield – Ansicht LÖTSEITE (Unterseite, zeigt zum Mega)',
                'Hier werden die Lötbahnen gezogen. Spalten/Reihen = Aufdruck. Spalte 1 links.',
                'Gilt nur mit Firmware-Variante „shield“ (pio run -e shield).']
    else:
        head = ['Lochraster-Shield – Ansicht BAUTEILSEITE (von oben, wie es auf dem Mega steckt)',
                'Hier werden die Bauteile gesteckt. Spalten/Reihen = Aufdruck. Spalte 1 rechts (gespiegelt zur Lötseite).',
                'Gestrichelt und durchscheinend = Lötbahnen UNTEN (Lötseite). Durchgezogen = Bauteile und Drähte OBEN.']
    w(f'<text x="24" y="38" font-size="22" font-weight="bold" fill="#1d1d1b">{head[0]}</text>')
    for i, t in enumerate(head[1:]):
        w(f'<text x="24" y="{62+i*20}" font-size="14" fill="#6b6b66">{t}</text>')
    w(f'<text x="24" y="{102}" font-size="14" fill="#c0392b" font-weight="bold">Vor dem Löten prüfen: Spalte {EVEN_COL} über den GERADEN Mega-Pins (22 … 52), Spalte {ODD_COL} über den ungeraden.</text>')
    w(f'<text x="24" y="{122}" font-size="13" fill="#0f6e8c">Blau, halbdurchsichtig: Arduino Mega darunter (Lage aus Pinout-Grafik geschätzt, ± 1 Raster).</text>')
    rect = lambda c0, r0, c1, r1, extra: w(f'<rect x="{min(X(c0),X(c1))}" y="{Y(r0)}" width="{abs(X(c1)-X(c0))}" height="{Y(r1)-Y(r0)}" {extra}/>')
    # Platine
    rect(0.45, 0.1, 26.55, 32.55, 'rx="6" fill="#f3e9dc" stroke="#b9a58c"')
    # Mega dahinter
    e, top, bot = MEGA_EDGE
    rect(e, top, NC + 0.5, bot, 'fill="#0f6e8c" fill-opacity="0.13" stroke="#0f6e8c" stroke-opacity="0.6" stroke-width="2" stroke-dasharray="8 5"')
    w(f'<text x="{X(NC)}" y="{Y(top)-8}" font-size="12" text-anchor="middle" fill="#0f6e8c" font-weight="bold">Arduino Mega</text>')
    w(f'<text x="{X(NC)}" y="{Y(bot)+16}" font-size="11" text-anchor="middle" fill="#0f6e8c">{"→" if solder else "←"} weiter zur USB-Buchse</text>')
    rect(18.5, 7.45, 20.5, 25.55, 'rx="3" fill="#0f2a33" fill-opacity="0.18"')
    for hdrs, name in ((DIG, 'Buchsenleiste D14–D21'), (ANA, 'Buchsenleiste A8–A15')):
        r = hdrs[0][1]
        rect(hdrs[0][0] - 0.5, r - 0.5, hdrs[-1][0] + 0.5, r + 0.5, 'rx="3" fill="#0f2a33" fill-opacity="0.18"')
        for c, r, t in hdrs:
            w(f'<rect x="{X(c)-5}" y="{Y(r)-5}" width="10" height="10" fill="#0f2a33" fill-opacity="0.35"/>')
            w(f'<text x="{X(c)}" y="{Y(r)+(-9 if r < 15 else 17)}" font-size="9" text-anchor="middle" fill="#0f6e8c">{t}</text>')
        w(f'<text x="{(X(hdrs[0][0])+X(hdrs[-1][0]))/2}" y="{Y(r)+(-24 if r < 15 else 34)}" font-size="11" text-anchor="middle" fill="#0f6e8c" font-weight="bold">{name} (Mega)</text>')
    # Spalten- und Reihennummern
    for c in range(1, 27):
        if c in (1, 10, 20) or c % 5 == 0 or c in (14, 17, 19, 23, 24):
            w(f'<text x="{X(c)}" y="{Y(1)-14}" font-size="10" text-anchor="middle" fill="#6b6b66">{c}</text>')
    for r in range(1, 33):
        w(f'<text x="{X(1) + (-20 if solder else 20)}" y="{Y(r)+4}" font-size="10" text-anchor="{"end" if solder else "start"}" fill="#6b6b66">{r}</text>')
    for c in range(1, 27):
        for r in range(1, 33):
            w(f'<circle cx="{X(c)}" cy="{Y(r)}" r="4" fill="#fff" stroke="#c9b79c"/>')
    # Loetbahnen: auf der Loetseite kraeftig, von oben durchscheinend und gestrichelt
    tstyle = 'stroke-width="6" opacity="0.75"' if solder else 'stroke-width="5" opacity="0.45" stroke-dasharray="7 5"'
    for net, paths in TR.items():
        col = NETCOL.get(net, '#8e44ad' if net in LABEL.values() else '#555')
        for p in paths:
            pts = ' '.join(f'{X(c)},{Y(r)}' for c, r in p)
            w(f'<polyline points="{pts}" fill="none" stroke="{col}" {tstyle} stroke-linecap="round" stroke-linejoin="round"/>')
    for a, b, net in ZW:      # Z-Draht oben: am Stiftende angeloetet, Nachbarloch nach unten
        col = NETCOL.get(net, '#8e44ad')
        w(f'<line x1="{X(a[0])}" y1="{Y(a[1])}" x2="{X(b[0])}" y2="{Y(b[1])}" stroke="{col}" stroke-width="{2.5 if solder else 4}" stroke-linecap="round"{" stroke-dasharray=\"4 3\"" if solder else ""}/>')
        w(f'<circle cx="{X(b[0])}" cy="{Y(b[1])}" r="4" fill="#fff" stroke="{col}" stroke-width="2.5"/>')
    # isolierte Drahtbruecken: auf der Bauteilseite durchgezogen, von unten gestrichelt
    for a, b, net in WIRES:
        dash = ' stroke-dasharray="7 4"' if solder else ''
        w(f'<path d="M{X(a[0])},{Y(a[1])} Q{(X(a[0])+X(b[0]))/2},{min(Y(a[1]),Y(b[1]))-40} {X(b[0])},{Y(b[1])}" fill="none" stroke="{NETCOL[net]}" stroke-width="3"{dash}/>')
    # Mega-Stiftleiste und Sockel
    for n in ['5V', 'GND'] + list(range(22, 54)):
        for c, r in (hdr(n) if isinstance(n, str) else [hdr(n)]):
            fill = {'5V':'#d68910','GND':'#1d1d1b'}.get(n, '#2e6fb7' if n in (VPP_EN, VCC_EN) else ('#bbb' if n == SPARE else '#555'))
            w(f'<circle cx="{X(c)}" cy="{Y(r)}" r="9" fill="{fill}"/>')
            w(f'<text x="{X(c)}" y="{Y(r)+3.5}" font-size="{8 if isinstance(n,str) else 9}" text-anchor="middle" fill="#fff" font-weight="bold">{n}</text>')
    for p in range(1, 33):
        c, r = sock(p)
        fill = {1:'#c0392b', 32:'#d68910', 16:'#1d1d1b'}.get(p, '#7d3c98')
        w(f'<circle cx="{X(c)}" cy="{Y(r)}" r="8.5" fill="{fill}"/>')
        w(f'<text x="{X(c)}" y="{Y(r)+3.5}" font-size="8.5" text-anchor="middle" fill="#fff" font-weight="bold">{p}</text>')
        d = out(c)
        w(f'<text x="{X(c)+13*d}" y="{Y(r)+4}" font-size="10" text-anchor="{"start" if d > 0 else "end"}">{LABEL[p]}</text>')
    if not solder:   # EPROM-Umriss mit Kerbe
        x0, x1 = sorted((X(SL), X(SR)))
        w(f'<rect x="{x0-14}" y="{Y(9)-16}" width="{x1-x0+28}" height="{Y(24)-Y(9)+32}" rx="4" fill="none" stroke="#7d3c98" stroke-width="1.5" stroke-dasharray="5 3"/>')
        w(f'<path d="M{(x0+x1)/2-10},{Y(9)-16} a10,10 0 0 0 20,0" fill="none" stroke="#7d3c98" stroke-width="2"/>')
        w(f'<text x="{x0-14}" y="{Y(26)+4}" font-size="11" fill="#7d3c98" font-weight="bold">EPROM-Umriss, Kerbe oben</text>')
    # Bauteile
    for name, legs in PARTS.items():
        pts = [(X(c), Y(r)) for c, r in legs.values()]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        if name == 'J1':
            w(f'<rect x="{min(xs)-12}" y="{min(ys)-12}" width="{max(xs)-min(xs)+24}" height="24" rx="3" fill="none" stroke="#1d1d1b" stroke-width="1.5"/>')
        elif name in TO92:
            order = TO92[name]; p0, p2 = PARTS[name][order[0]], PARTS[name][order[2]]
            dx, dy = X(p2[0]) - X(p0[0]), Y(p2[1]) - Y(p0[1]); L = (dx*dx + dy*dy) ** 0.5
            sg = -1 if solder else 1                       # von unten gesehen ist die Haendigkeit gespiegelt
            nx, ny = -dy / L * sg, dx / L * sg             # zeigt zur flachen Seite
            mx, my = (X(p0[0]) + X(p2[0])) / 2, (Y(p0[1]) + Y(p2[1])) / 2
            R, f = 1.25 * S, 0.45 * S
            ax, ay = mx + nx*f - dx/L*R, my + ny*f - dy/L*R
            bx, by = mx + nx*f + dx/L*R, my + ny*f + dy/L*R
            w(f'<path d="M{ax:.1f},{ay:.1f} L{bx:.1f},{by:.1f} A{R},{R} 0 0 {0 if sg > 0 else 1} {ax:.1f},{ay:.1f} Z" fill="#555" fill-opacity="{0.1 if solder else 0.22}" stroke="#1d1d1b" stroke-width="{1.5 if solder else 2.5}"{" stroke-dasharray=\"4 2\"" if solder else ""}/>')
        elif name[0] == 'R':          # stehend: Koerper auf Bein a, Draht zu b
            (ac, ar), (bc, br) = legs['a'], legs['b']
            w(f'<line x1="{X(ac)}" y1="{Y(ar)}" x2="{X(bc)}" y2="{Y(br)}" stroke="#8a6d3b" stroke-width="2"/>')
            w(f'<circle cx="{X(ac)}" cy="{Y(ar)}" r="10" fill="#e8d9b5" fill-opacity="{0.35 if solder else 0.7}" stroke="#8a6d3b" stroke-width="1.5"{" stroke-dasharray=\"4 2\"" if solder else ""}/>')
        else:                         # Diode: Koerper mit Ring auf der Kathodenseite
            (kc, kr), (ac, ar) = legs['K'], legs['A']
            x1, y1, x2, y2 = X(ac), Y(ar), X(kc), Y(kr)
            w(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#7a6a55" stroke-width="2"/>')
            if abs(x2 - x1) > S:      # liegend
                cx, cy = (x1 + x2) / 2, y1; s = 1 if x2 > x1 else -1
                w(f'<rect x="{cx-22}" y="{cy-7}" width="44" height="14" rx="3" fill="#3a3a3a" fill-opacity="{0.25 if solder else 0.55}" stroke="#3a3a3a"/>')
                w(f'<rect x="{cx+s*22-(8 if s > 0 else 0)}" y="{cy-7}" width="8" height="14" fill="#ccc" stroke="#3a3a3a"/>')
            else:                     # stehend: Koerper auf der Kathode, Ring unten
                w(f'<circle cx="{x2}" cy="{y2}" r="10" fill="#3a3a3a" fill-opacity="{0.25 if solder else 0.55}" stroke="#3a3a3a"/>')
                w(f'<circle cx="{x2}" cy="{y2}" r="6" fill="none" stroke="#ccc" stroke-width="3"/>')
    for name, legs in PARTS.items():
        for leg, (c, r) in legs.items():
            w(f'<circle cx="{X(c)}" cy="{Y(r)}" r="4.5" fill="#1d1d1b"/>')
            w(f'<text x="{X(c)}" y="{Y(r)-7}" font-size="9" text-anchor="middle" fill="#1d1d1b" font-weight="bold">{leg.split()[0] if name != "J1" else leg.replace(" V","")}</text>')
    for a, b, net in WIRES:
        for c, r in (a, b):
            w(f'<circle cx="{X(c)}" cy="{Y(r)}" r="5" fill="#fff" stroke="{NETCOL[net]}" stroke-width="2.5"/>')
    # Bauteilnamen (mit Hilfslinie)
    for name, (c, r) in NAMEPOS.items():
        legs = list(PARTS[name].values()); tx, ty = legs[len(legs)//2]
        d = 1 if X(c) > X(tx) else -1
        w(f'<line x1="{X(c)}" y1="{Y(r)}" x2="{X(tx)}" y2="{Y(ty)}" stroke="#999" stroke-width="1"/>')
        w(f'<rect x="{X(c)-(0 if d > 0 else 82)}" y="{Y(r)-9}" width="82" height="17" rx="3" fill="#fff" stroke="#999"/>')
        w(f'<text x="{X(c)+4*d}" y="{Y(r)+4}" font-size="11" text-anchor="{"start" if d > 0 else "end"}" font-weight="bold">{name}</text>')
    # Legende
    LX, LY = OX + (NC - 1) * S + 40, Y(10)
    w(f'<text x="{LX}" y="{LY-18}" font-size="14" font-weight="bold">Legende</text>')
    i = 0
    if True:
        if not solder:
            w(f'<text x="{LX}" y="{LY+4}" font-size="12" font-style="italic">Lötbahnen unten (durchscheinend):</text>'); i += 1
        for colr, t in [('#8e44ad','Signal-Bahn (je Reihe gerade)'),('#1d1d1b','GND'),('#d68910','5 V / 6,25 V / VCC'),
                        ('#c0392b','12,75 V / VPP'),('#2e6fb7','Steuerleitung 22 / 23'),('#555','Bahn innerhalb der Stufen')]:
            w(f'<line x1="{LX}" y1="{LY+i*22}" x2="{LX+28}" y2="{LY+i*22}" stroke="{colr}" stroke-width="6" opacity="{0.6 if solder else 0.45}" stroke-linecap="round"{"" if solder else " stroke-dasharray=\"7 5\""}/>')
            w(f'<text x="{LX+38}" y="{LY+i*22+4}" font-size="12">{t}</text>'); i += 1
    w(f'<path d="M{LX},{LY+i*22} h28" stroke="#1d1d1b" stroke-width="2.5"{" stroke-dasharray=\"7 4\"" if solder else ""}/>')
    w(f'<text x="{LX+38}" y="{LY+i*22+4}" font-size="12">isolierter Draht (Bauteilseite)</text>'); i += 1
    w(f'<line x1="{LX}" y1="{LY+i*22}" x2="{LX+20}" y2="{LY+i*22}" stroke="#8e44ad" stroke-width="{2.5 if solder else 4}"{" stroke-dasharray=\"4 3\"" if solder else ""}/><circle cx="{LX+24}" cy="{LY+i*22}" r="4" fill="#fff" stroke="#8e44ad" stroke-width="2.5"/>')
    w(f'<text x="{LX+38}" y="{LY+i*22+4}" font-size="12">Z-Draht oben, Kreis = Loch nach unten</text>'); i += 1
    w(f'<path d="M{LX},{LY+i*22+6} h28 a14,14 0 0 0 -28,0 Z" fill="#555" fill-opacity="0.22" stroke="#1d1d1b" stroke-width="2"/>')
    w(f'<text x="{LX+38}" y="{LY+i*22+4}" font-size="12">TO-92 von {"unten" if solder else "oben"}: Kante = flache Seite</text>'); i += 1
    if solder:
        notes = ['Lötbahnen:', '• 2 Löcher: Lötbrücke genügt.', '• ab 3 Löchern: blanken Draht', '  (Silberdraht) auflegen und an', '  jedem Loch verlöten.',
                 '• Benachbarte Reihen dürfen sich', '  nicht berühren – nachmessen.', '',
                 '• Mega-Stifte (Sp. 19/20) unten', '  NICHT löten: der Kunststoff', '  liegt hier, Anschluss nur über', '  die Z-Drähte oben.', '',
                 'Über der Mega-Buchsenleiste', 'D14–D21 (Reihe 7–9, ab Sp. 21)', 'dort läuft VPP (12,75 V):', 'Isolierband auf die Unterseite.']
    else:
        notes = ['Einbau:', '• Mega-Stiftleiste von UNTEN:', '  Kunststoff zwischen Shield und', '  Mega, kurze Enden ragen oben', '  heraus. Kunststoff ankleben.',
             '• Z-Drähte: oben am Stiftende', '  anlöten, durchs Nachbarloch', '  nach unten, unten weiter als Bahn.', '• Kerbe des EPROMs zu Reihe 1.',
                 '• Widerstände stehend (Körper', '  auf dem Kreis, Draht zurück).', '• D2 liegend, D1 stehend:', '  Körper auf K, Ring unten.',
                 '• Transistoren: flache Seite wie', '  gezeichnet. Beschriftung E/B/C', '  am Loch ist maßgeblich.', '• Pin 52 frei (grau).',
                 '• Spalte 1 hängt am Anschluss-', '  feld, nicht benutzen.',
                 '• Das EPROM liegt über den Z-', '  Drähten (oben nur ca. 1,5 mm', '  Stiftende + Draht).']
    for k, t in enumerate(notes):
        w(f'<text x="{LX}" y="{LY+i*22+30+k*19}" font-size="12" font-weight="{"bold" if k == 0 or t.endswith(":") else "normal"}">{t}</text>')
    w('</svg>')
    open(path, 'w', encoding='utf-8').write('\n'.join(o))

NETCOL = {'GND':'#1d1d1b','5V':'#d68910','VCC':'#d68910','+6V25':'#d68910','VPP':'#c0392b','+12V75':'#c0392b',
          'VPP_EN':'#2e6fb7','VCC_EN':'#2e6fb7'}
NAMEPOS = {'J1':(10,1),'Q1 BC337':(26,2),'R1 1k':(10,3),'R2 1k':(26,3),'Q2 BC327':(26,4),'R3 10k':(26,5),
           'D2 1N5819':(26,6),'D1 1N5819':(10,6),'Q4 S8550':(10,4),'R6 10k':(10,2),'R5 1k':(10,5),'Q3 S8050':(10,7),'R4 1k':(10,8)}
svg(sys.argv[1], False)   # nur Ansicht von oben; svg(pfad, True) zeichnet bei Bedarf die Loetseite
# ---------- Markdown ----------
fm = lambda h: f'{h[0]}/{h[1]}'
print('| Reihe | Sockel links (Sp. 17) | Mega links (Sp. 19) | Mega rechts (Sp. 20) | Sockel rechts (Sp. 23) |')
print('| :--- | :--- | :--- | :--- | :--- |')
print('| 8 | – | 5V | 5V | – |')
for r in range(9, 26):
    def cell(c):
        p = next((p for p in range(1, 33) if sock(p) == (c, r)), None)
        return f'Pin {p} {LABEL[p]}' if p else '–'
    if r == 25:
        print('| 25 | – | GND | GND | – |'); continue
    n_odd, n_even = 23 + 2*(r-9), 22 + 2*(r-9)
    def mega(n):
        return f'`{n}`' + {VPP_EN:' VPP_EN', VCC_EN:' VCC_EN', SPARE:' frei'}.get(n, '')
    print(f'| {r} | {cell(SL)} | {mega(n_odd)} | {mega(n_even)} | {cell(SR)} |')
print('\n| Bauteil | Bein → Loch (Sp./R.) |\n| :--- | :--- |')
for name, legs in PARTS.items():
    print(f'| {name} | ' + ', '.join(f'{k} {fm(v)}' for k, v in legs.items()) + ' |')
print('\n| Netz | Lötbahn (Loch → Loch) |\n| :--- | :--- |')
for net, paths in TR.items():
    if net in LABEL.values() and net not in ('VPP', 'VCC'): continue
    for path in paths:
        print(f'| {net} | {fm(path[0])} → {fm(path[-1])} ({len(path)} Löcher) |')
for a, b, net in WIRES:
    print(f'| {net} | Draht {fm(a)} → {fm(b)} |')
# ---------- C-Pinlisten ----------
inv = {LABEL[p]: n for p, n in MEGA.items()}
print('DATA', [inv[f'Q{i}'] for i in range(8)], file=sys.stderr)
print('ADDR', [inv[f'A{i}'] for i in range(19)], file=sys.stderr)
print('CE', inv['E'], 'OE', inv['G'], file=sys.stderr)
