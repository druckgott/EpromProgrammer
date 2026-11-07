# Lochraster-Shield (README 4.8): Mega-Stiftleiste in der Mitte, Sockelleisten links/rechts, je Reihe eine gerade Loetbahn.
# Koordinaten (Spalte, Reihe) = Aufdruck der Platine, Ansicht LOETSEITE. Prueft Netze (jedes Loch ein Netz, jedes Netz verbunden).
# Aufruf: python -X utf8 tools/lochraster_shield.py images/lochraster_shield.svg  -> SVG, Markdown-Tabellen (stdout), C-Pinlisten fuer defines.h (stderr)
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
 'D1 1N5819': {'K':(19,7), 'A':(20,7)},
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
 'GND':    [[sock(16), (23,25), (22,25), (21,25), (20,25), (19,25), (18,25), (17,25), (16,25)] + [(16, r) for r in range(24, 6, -1)],
            [(16,8), (15,8)], [(19,2), (20,2), (20,1)]],
 '5V':     [[(20,8), (20,7)]],
 'VCC':    [[(17,9), (17,8), (17,7), (17,6), (17,5)], [(19,7), (18,7), (17,7)]],
 'VPP':    [[(23,9), (23,8), (23,7), (23,6), (23,5)]],
 'VPP_EN': [[(20,9), (21,9), (21,8), (21,7), (21,6), (21,5), (21,4)]],
 'B1':     [[(21,3), (21,2)]],
 'C1':     [[(22,2), (22,3)]],
 'B2':     [[(22,4), (23,4), (24,4)]],
 '+12V75': [[(21,1), (22,1), (23,1), (23,2), (23,3), (24,3)]],
 'VCC_EN': [[(19,9), (18,9), (18,8)]],
 'B3':     [[(14,7), (15,7)]],
 'C3':     [[(15,6), (15,5)]],
 'B4':     [[(15,4), (16,4), (17,4)]],
 '+6V25':  [[(19,1), (18,1), (17,1), (17,2), (17,3), (16,3)]],
}
for p, n in MEGA.items():
    (c, r), (hc, _) = sock(p), hdr(n)
    step = 1 if hc > c else -1
    TR[LABEL[p]] = [[(x, r) for x in range(c, hc + step, step)]]
# Isolierte Drahtbruecken (Bauteilseite)
WIRES = [((19,2), (16,7), 'GND'), ((18,8), (14,8), 'VCC_EN')]

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
for a, b, net in WIRES: take(a, net); take(b, net)
used_by_part_or_sock = {h for legs in PARTS.values() for h in legs.values()} | {sock(p) for p in range(1, 33)}
parent = {}
def f(x):
    parent.setdefault(x, x)
    while parent[x] != x: x = parent[x]
    return x
for paths in TR.values():
    for path in paths:
        for a, b in zip(path, path[1:]): parent[f(a)] = f(b)
for a, b, _ in WIRES: parent[f(a)] = f(b)
parent[f(hdr('5V')[0])] = f(hdr('5V')[1])             # beide 5V-Stifte sind im Mega verbunden
for net, legs in NETLEGS.items():
    roots = {f(h) for h in legs}
    assert len(roots) == 1, ('Netz nicht verbunden', net, legs)
assert hdr(SPARE) not in hole, 'Ersatz-Pin belegt'
print('OK: Netze geprueft', file=sys.stderr)

# ---------- SVG ----------
S, OX, OY = 28, 70, 150
X = lambda c: OX + (c - 1) * S
Y = lambda r: OY + (r - 1) * S
NETCOL = {'GND':'#1d1d1b','5V':'#d68910','VCC':'#d68910','+6V25':'#d68910','VPP':'#c0392b','+12V75':'#c0392b',
          'VPP_EN':'#2e6fb7','VCC_EN':'#2e6fb7'}
o = []; w = o.append
W, H = OX + 26 * S + 360, OY + 33 * S + 20
w(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Segoe UI, Helvetica, Arial, sans-serif">')
w(f'<rect width="{W}" height="{H}" fill="#fff"/>')
w('<text x="24" y="38" font-size="22" font-weight="bold" fill="#1d1d1b">Lochraster-Shield v2 – Ansicht LÖTSEITE</text>')
w('<text x="24" y="62" font-size="14" fill="#6b6b66">Spalten/Reihen = Aufdruck der Platine. Mega-Stiftleiste in der Mitte, EPROM-Leisten links/rechts, je Reihe eine gerade Lötbahn.</text>')
w('<text x="24" y="82" font-size="14" fill="#6b6b66">Gilt nur mit Firmware-Variante „shield“ (pio run -e shield). Von der Bauteilseite aus ist alles spiegelverkehrt.</text>')
w(f'<text x="24" y="104" font-size="14" fill="#c0392b" font-weight="bold">Vor dem Löten prüfen: Spalte {EVEN_COL} muss über den GERADEN Mega-Pins (22 … 52) liegen, Spalte {ODD_COL} über den ungeraden.</text>')
w(f'<rect x="{X(1)-16}" y="{Y(1)-26}" width="{26*S+4}" height="{32*S+16}" rx="6" fill="#f3e9dc" stroke="#b9a58c"/>')
w(f'<rect x="{X(14)-12}" y="{Y(1)-12}" width="{11*S-4}" height="{25*S-4}" rx="4" fill="none" stroke="#2e6fb7" stroke-dasharray="6 4"/>')
w(f'<text x="{X(14)-12}" y="{Y(27)+2}" font-size="11" fill="#2e6fb7">belegt: Spalte 14–24, Reihe 1–25 · Rest frei</text>')
for c in range(1, 27):
    if c in (1, 10, 20) or c % 5 == 0 or c in (14, 17, 19, 23, 24):
        w(f'<text x="{X(c)}" y="{Y(1)-10}" font-size="10" text-anchor="middle" fill="#6b6b66">{c}</text>')
for r in range(1, 33):
    w(f'<text x="{X(1)-20}" y="{Y(r)+4}" font-size="10" text-anchor="end" fill="#6b6b66">{r}</text>')
for c in range(1, 27):
    for r in range(1, 33):
        w(f'<circle cx="{X(c)}" cy="{Y(r)}" r="4" fill="#fff" stroke="#c9b79c"/>')
def draw_traces():   # nach den Bauteilen zeichnen, damit nichts verdeckt wird
    for net, paths in TR.items():
        col = NETCOL.get(net, '#8e44ad' if net in LABEL.values() else '#555')
        for path in paths:
            pts = ' '.join(f'{X(c)},{Y(r)}' for c, r in path)
            w(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" opacity="0.75"/>')
    for a, b, net in WIRES:
        w(f'<path d="M{X(a[0])},{Y(a[1])} Q{(X(a[0])+X(b[0]))/2},{min(Y(a[1]),Y(b[1]))-40} {X(b[0])},{Y(b[1])}" fill="none" stroke="{NETCOL[net]}" stroke-width="3" stroke-dasharray="7 4"/>')
# Bauteile
for name, legs in PARTS.items():
    pts = list(legs.values()); xs = [X(c) for c, _ in pts]; ys = [Y(r) for _, r in pts]
    if name == 'J1':
        w(f'<rect x="{min(xs)-12}" y="{min(ys)-12}" width="{max(xs)-min(xs)+24}" height="24" rx="3" fill="none" stroke="#1d1d1b" stroke-width="1.5"/>')
    elif name[0] == 'Q':
        w(f'<rect x="{min(xs)-12}" y="{min(ys)-12}" width="{max(xs)-min(xs)+24}" height="{max(ys)-min(ys)+24}" rx="11" fill="#eeeeec" fill-opacity="0.35" stroke="#1d1d1b" stroke-width="1.5" stroke-dasharray="4 2"/>')
    elif name[0] == 'R':
        w(f'<rect x="{min(xs)-9}" y="{min(ys)-9}" width="{max(xs)-min(xs)+18}" height="{max(ys)-min(ys)+18}" rx="8" fill="#e8d9b5" fill-opacity="0.35" stroke="#8a6d3b" stroke-width="1.5" stroke-dasharray="4 2"/>')
    else:
        w(f'<line x1="{min(xs)}" y1="{min(ys)}" x2="{max(xs)}" y2="{max(ys)}" stroke="#7a6a55" stroke-width="2"/>')
        cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
        bw = 44 if max(xs)-min(xs) > S else 14
        bh = 14 if max(xs)-min(xs) > S else 14
        w(f'<rect x="{cx-bw/2}" y="{cy-bh/2}" width="{bw}" height="{bh}" rx="3" fill="#3a3a3a" fill-opacity="0.35" stroke="#3a3a3a" stroke-dasharray="4 2"/>')
def draw_strips():
    w(f'<rect x="{X(ODD_COL)-11}" y="{Y(8)-11}" width="{2*S-6}" height="{18*S-6}" rx="3" fill="#2e6fb7" opacity="0.12" stroke="#2e6fb7" stroke-width="2"/>')
    for col in (SL, SR):
        w(f'<rect x="{X(col)-11}" y="{Y(9)-11}" width="22" height="{16*S-6}" rx="3" fill="#7d3c98" opacity="0.10" stroke="#7d3c98"/>')
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
        if p <= 16: w(f'<text x="{X(c)+13}" y="{Y(r)+4}" font-size="10" text-anchor="start">{LABEL[p]}</text>')
        else:       w(f'<text x="{X(c)-13}" y="{Y(r)+4}" font-size="10" text-anchor="end">{LABEL[p]}</text>')
    w(f'<text x="{X(SL)-14}" y="{Y(26)+16}" font-size="11" text-anchor="middle">Sockel</text>')
    w(f'<text x="{(X(ODD_COL)+X(EVEN_COL))/2}" y="{Y(26)+16}" font-size="11" text-anchor="middle" fill="#2e6fb7" font-weight="bold">Mega 2×18</text>')
    w(f'<text x="{X(SR)+14}" y="{Y(26)+16}" font-size="11" text-anchor="middle">Sockel</text>')
draw_traces()
draw_strips()
for name, legs in PARTS.items():
    for leg, (c, r) in legs.items():
        w(f'<circle cx="{X(c)}" cy="{Y(r)}" r="4.5" fill="#1d1d1b"/>')
        w(f'<text x="{X(c)}" y="{Y(r)-7}" font-size="8" text-anchor="middle" fill="#1d1d1b" font-weight="bold">{leg.split()[0] if name != "J1" else leg.replace(" V","")}</text>')
# Bauteilnamen an der Seite (mit Hilfslinie)
NAMEPOS = {'J1':(10,1),'Q1 BC337':(26,2),'R1 1k':(10,3),'R2 1k':(26,3),'Q2 BC327':(26,4),'R3 10k':(26,5),
           'D2 1N5819':(26,6),'D1 1N5819':(10,6),'Q4 S8550':(10,4),'R6 10k':(10,2),'R5 1k':(10,5),'Q3 S8050':(10,7),'R4 1k':(10,8)}
for name, (c, r) in NAMEPOS.items():
    legs = list(PARTS[name].values()); tx, ty = legs[len(legs)//2]
    anchor = 'start' if c > 20 else 'end'
    w(f'<line x1="{X(c)}" y1="{Y(r)}" x2="{X(tx)}" y2="{Y(ty)}" stroke="#999" stroke-width="1"/>')
    w(f'<rect x="{X(c)-(0 if anchor=="start" else 78)}" y="{Y(r)-9}" width="78" height="17" rx="3" fill="#fff" stroke="#999"/>')
    w(f'<text x="{X(c)+(4 if anchor=="start" else -4)}" y="{Y(r)+4}" font-size="11" text-anchor="{anchor}" font-weight="bold">{name}</text>')
# Legende
LX, LY = X(26) + 100, Y(9)
leg = [('#8e44ad','Signal-Bahn (je Reihe gerade)'),('#1d1d1b','GND'),('#d68910','5 V / 6,25 V / VCC'),
       ('#c0392b','12,75 V / VPP'),('#2e6fb7','Steuerleitung 22 / 23'),('#555','Bahn innerhalb der Stufen')]
w(f'<text x="{LX}" y="{LY-18}" font-size="14" font-weight="bold">Legende</text>')
for i, (colr, t) in enumerate(leg):
    w(f'<line x1="{LX}" y1="{LY+i*22}" x2="{LX+28}" y2="{LY+i*22}" stroke="{colr}" stroke-width="6" opacity="0.6" stroke-linecap="round"/>')
    w(f'<text x="{LX+38}" y="{LY+i*22+4}" font-size="12">{t}</text>')
w(f'<path d="M{LX},{LY+6*22} h28" stroke="#1d1d1b" stroke-width="2.5" stroke-dasharray="7 4"/>')
w(f'<text x="{LX+38}" y="{LY+6*22+4}" font-size="12">isolierter Draht (Bauteilseite)</text>')
notes = ['Hinweise:', '• Kerbe des EPROMs zeigt zu Reihe 1.', '• Pin 52 frei (grau).', '• Widerstände stehend, Dioden:',
         '  D2 liegend, D1 stehend.', '• Transistor-Beine nach Loch-Liste,', '  nicht nach Bild-Ausrichtung.',
         '• Spalte 1 hängt am Anschlussfeld,', '  nicht benutzen.', '• Unterseite gegen den Mega mit', '  Isolierband abdecken.']
for i, t in enumerate(notes):
    w(f'<text x="{LX}" y="{LY+190+i*19}" font-size="12" font-weight="{"bold" if i==0 else "normal"}">{t}</text>')
w('</svg>')
open(sys.argv[1], 'w', encoding='utf-8').write('\n'.join(o))

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
