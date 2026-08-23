#!/usr/bin/env python3
"""Compose a restaurant dish from AUSNUT ingredients.

Nutrients do not evaporate; water does. So a dish is the sum of what went into
it, divided by what came out of the pan — which is why every dish below carries
a raw ingredient list and one 'served' weight, and nothing else is guessed.
Emits the same pipe-delimited line the FOODS table uses, micros and all.
"""
import io, re, sys

SRC = 'index.html'
MICROS = 27

def table():
    h = io.open(SRC, encoding='utf-8').read()
    rows = {}
    for line in h.split('\n'):
        if line.count('|') < 12: continue
        p = line.split('|')
        if not re.match(r'^F\d{6}$', p[-1].strip()): continue
        rows[p[-1].strip()] = p
    return rows

T = table()

def nut(key):
    p = T[key]
    v = {'name': p[0], 'kj': float(p[2]), 'p': float(p[3]), 'f': float(p[4]),
         'sat': float(p[5]), 'c': float(p[6]), 'sug': float(p[7]),
         'fib': float(p[8]), 'na': float(p[9]), 'alc': float(p[10])}
    v['m'] = [float(p[12 + i] or 0) for i in range(MICROS)]
    return v

def compose(name, cat, items, served, key, note):
    tot = {k: 0.0 for k in ('kj','p','f','sat','c','sug','fib','na','alc')}
    mt = [0.0] * MICROS
    raw = 0.0
    for k, grams in items:
        n = nut(k); f = grams / 100.0; raw += grams
        for x in tot: tot[x] += n[x] * f
        for i in range(MICROS): mt[i] += n['m'][i] * f
    per = 100.0 / served
    def g(x, dp=2):
        v = round(x * per, dp)
        return ('%g' % v)
    line = '|'.join([name, cat] +
        [g(tot['kj'], 0)] + [g(tot[x]) for x in ('p','f','sat','c','sug','fib')] +
        [g(tot['na'], 0), g(tot['alc'])] + ['0'] +
        [g(v, 3) for v in mt] + [key])
    kcal = tot['kj'] / 4.184
    print('%-34s raw %4.0f g -> served %4.0f g | %5.0f kJ (%4.0f kcal) total, '
          'P %.0f C %.0f F %.0f, Na %.0f mg' %
          (name.split(',')[0], raw, served, tot['kj'], kcal, tot['p'], tot['c'], tot['f'], tot['na']))
    return line

def borrow(name, cat, src, served, key, portions):
    """No composition at all — FSANZ analysed this food, it just isn't filed
    under the name anyone says out loud, and it has no per-piece portion."""
    p = T[src]
    line = '|'.join([name, cat] + p[2:12] + p[12:12+MICROS] + [key])
    print('%-34s from %s (%s)' % (name.split(',')[0], src, p[0][:44]))
    return line

DISHES = [
 dict(name='Shengjian bao, pork, pan-fried (restaurant)', cat='91', key='R000001',
      served=300,
      portions='bun:75;serve of four:300',
      items=[('F004007',115),('F009527',65),('F007057',90),('F006862',25),
             ('F008936',30),('F006250',12),('F004213',5),('F008065',10),
             ('F008976',4),('F006187',4),('F006191',14),('F008214',3)]),
 dict(name='Liangmian, cold sesame noodles (restaurant)', cat='91', key='R000002',
      served=454,
      portions='bowl:454;half bowl:227',
      items=[('F006048',250),('F009076',32),('F008065',16),('F009498',10),
             ('F008976',5),('F004193',5),('F006187',12),('F003320',70),
             ('F008806',40),('F006250',10),('F008214',4)]),
 dict(name='Cumin lamb, sliced, with bean sprouts (restaurant)', cat='91', key='R000003',
      served=310,
      portions='serve:310;share of a plate:155',
      items=[('F005077',200),('F006191',18),('F003327',5),('F002893',3),
             ('F004193',8),('F008806',110),('F006250',30),('F003192',6),
             ('F008065',10),('F008976',2)]),
]

def note(d):
    parts = sorted(d['items'], key=lambda x: -x[1])[:6]
    names = []
    for k, grams in parts:
        n = nut(k)['name'].split(',')
        short = n[0].strip()
        if len(n) > 1 and n[1].strip() in ('white','wheat','peeled','common','bean','fresh'):
            short += ' ' + n[1].strip()
        names.append('%d g %s' % (grams, short.lower()))
    return ('Composed from AUSNUT ingredients \u2014 ' + ', '.join(names) +
            ' and the rest \u2014 cooked down to %d g. An estimate of a restaurant serve, '
            'not an analysis of one. Salt is the least certain number here: kitchens '
            'season harder than a recipe does.') % d['served']

# ---- named from what FSANZ already analysed --------------------------------
BORROWED = [
 dict(name='Har gow, prawn dumpling, steamed (yum cha)', src='F003654', key='R000010',
      portions='piece:22;serve of four:88', served=100,
      note='FSANZ analysed a steamed seafood dumpling; this is that food under the name '
           'it goes by on a trolley, portioned by the piece.'),
 dict(name='Siu mai, pork and prawn dumpling, steamed (yum cha)', src='F003652', key='R000011',
      portions='piece:25;serve of four:100', served=100,
      note='FSANZ analysed a steamed meat dumpling; this is that food named and portioned '
           'the way it arrives.'),
 dict(name='Gow gee, pan-fried dumpling / potsticker / gyoza (yum cha)', src='F003651', key='R000012',
      portions='piece:28;serve of five:140', served=100,
      note='FSANZ analysed a fried meat dumpling. Potsticker, guotie and gyoza are the same '
           'thing under other names.'),
 dict(name='Wonton, deep-fried (yum cha)', src='F003651', key='R000013',
      portions='piece:16;serve of six:96', served=100,
      note='FSANZ analysed a fried meat dumpling. A wonton is a smaller, thinner-skinned one, '
           'so the per-100 g figures hold and only the piece weight differs.'),
 dict(name='Vegetable dumpling, steamed (yum cha)', src='F003655', key='R000014',
      portions='piece:25;serve of four:100', served=100,
      note='FSANZ analysed a steamed vegetable dumpling, portioned by the piece.'),
 dict(name='Char siu bao, BBQ pork bun, steamed (yum cha)', src='F008837', key='R000015',
      portions='bun:85;serve of three:255', served=100,
      note='FSANZ analysed a savoury steamed pork bun, which is what this is.'),
 dict(name='Salt and pepper squid (yum cha)', src='F008824', key='R000016',
      portions='serve:180;small serve:120', served=100,
      note='FSANZ analysed crumbed squid deep fried at a takeaway outlet.'),
]

# ---- composed, because FSANZ has no equivalent -----------------------------
MORE = [
 dict(name='Xiao long bao, soup dumpling, steamed (yum cha)', cat='91', key='R000020',
      served=110, portions='piece:28;serve of four:110',
      note='36 g of flour and 18 g of water for a thin unleavened skin, 36 g of pork mince '
           'with 8 g of belly, and 20 g of stock set as aspic that melts back to soup.',
      items=[('F004007',36),('F009527',18),('F007057',36),('F006862',8),
             ('F008936',20),('F004213',2),('F008065',4),('F008976',1)]),
 dict(name='Cheung fun, prawn rice noodle roll (yum cha)', cat='91', key='R000021',
      served=320, portions='roll:107;serve of three:320',
      note='55 g of rice flour and 12 g of cornflour steamed into sheets with the water, '
           '60 g of prawn inside, and 16 g of sweet soy poured over at the table.',
      items=[('F003998',55),('F003988',12),('F009527',210),('F007433',60),
             ('F006191',6),('F008065',16),('F008976',4),('F006187',3)]),
 dict(name='Lo mai gai, sticky rice in lotus leaf (yum cha)', cat='91', key='R000022',
      served=240, portions='parcel:240;half parcel:120',
      note='180 g of cooked rice — FSANZ has no glutinous rice, and plain white is within a '
           'few per cent of it — with 45 g of chicken thigh, shiitake, soy and a little oil.',
      items=[('F007661',180),('F002806',45),('F005956',20),('F006191',10),
             ('F008065',8),('F008976',2),('F006250',5)]),
 dict(name='Lo bak go, turnip cake, pan-fried (yum cha)', cat='91', key='R000023',
      served=300, portions='piece:55;serve of three:165',
      note='200 g of daikon with 60 g of rice flour and 10 g of cornflour to set it, bacon '
           'standing in for lap cheong, dried prawn and spring onion through it, then 10 g of '
           'oil in the pan.',
      items=[('F007608',200),('F003998',60),('F003988',10),('F009527',60),
             ('F000228',15),('F007433',8),('F006250',5),('F006191',10)]),
 dict(name='Wu gok, taro puff, deep-fried (yum cha)', cat='91', key='R000024',
      served=200, portions='piece:45;serve of three:135',
      note='120 g of taro mashed with 25 g of starch and 22 g of fat into the lacy shell, '
           '40 g of pork mince and shiitake inside, and 18 g of oil taken up in the fryer.',
      items=[('F009093',120),('F003988',25),('F006191',40),('F007057',40),
             ('F005956',12),('F008065',4),('F008976',2)]),
 dict(name='Egg tart, dan tat (yum cha)', cat='91', key='R000025',
      served=55, portions='tart:55;two tarts:110',
      note='24 g of shortcrust under a custard of 16 g egg, 13 g milk and 7 g sugar. Baked '
           'down to a 55 g tart.',
      items=[('F006507',24),('F003729',16),('F005634',13),('F008976',7),('F009527',5)]),
 dict(name='Custard bun, lai wong bao, steamed (yum cha)', cat='91', key='R000026',
      served=65, portions='bun:65;serve of three:195',
      note='30 g of flour and 16 g of water for the bun, filled with a custard of egg, milk, '
           'butter and 8 g of sugar.',
      items=[('F004007',30),('F009527',16),('F008976',8),('F003729',8),
             ('F001973',6),('F005634',6)]),
 dict(name='Sesame ball, jian dui, deep-fried (yum cha)', cat='91', key='R000027',
      served=55, portions='ball:55;serve of three:165',
      note='22 g of rice flour rolled in sesame, around a sweet bean paste. FSANZ has no '
           'adzuki, so cooked red kidney with sugar stands in — near enough on energy, '
           'protein and fibre.',
      items=[('F003998',22),('F009527',10),('F000451',14),('F008976',7),
             ('F008214',4),('F006191',7)]),
 dict(name='Spare ribs in black bean, steamed (yum cha)', cat='91', key='R000028',
      served=165, portions='serve:165;half serve:82',
      note='180 g of untrimmed spare rib steamed with soy, garlic, sugar and a little oil — '
           'FSANZ has no fermented black bean, and the soy carries most of what it brings.',
      items=[('F007117',180),('F008065',12),('F004193',5),('F008976',4),
             ('F006191',4),('F003988',3)]),
 dict(name='Beef ball, steamed (yum cha)', cat='91', key='R000029',
      served=120, portions='ball:30;serve of four:120',
      note='140 g of beef mince with cornflour and spring onion, steamed on bean curd skin. '
           'No coriander stalk in the numbers, only in the flavour.',
      items=[('F000677',140),('F003988',8),('F006250',10),('F008065',6),
             ('F003192',4),('F006187',2)]),
 dict(name='Mango pancake (yum cha)', cat='91', key='R000030',
      served=100, portions='pancake:100;two pancakes:200',
      note='55 g of mango and 28 g of whipped cream in a thin crepe of flour, egg and milk.',
      items=[('F005299',55),('F003251',28),('F004007',12),('F003729',6),
             ('F005634',10),('F008976',4)]),
 dict(name='Chicken feet, braised (phoenix claws, yum cha)', cat='91', key='R000031',
      served=120, portions='serve:120;half serve:60',
      note='120 g of cooked chicken feet braised in soy, sugar, garlic and oil. Edible '
           'portion — the bone is not in the weight.',
      items=[('F002670',120),('F008065',10),('F008976',4),('F006191',8),('F004193',3)]),
]

DISHES = DISHES + MORE

out, notes, meas = [], [], []
for d in BORROWED:
    out.append(borrow(d['name'], '91', d['src'], d['served'], d['key'], d['portions']))
    notes.append("  %s: '%s'," % (d['key'], d['note'].replace("'", "\\'")))
    meas.append('%s|%s' % (d['key'], d['portions']))
for d in DISHES:
    out.append(compose(d['name'], d['cat'], d['items'], d['served'], d['key'], ''))
    notes.append("  %s: '%s'," % (d['key'], d.get('note', note(d)).replace("'", "\\'")))
    meas.append('%s|%s' % (d['key'], d['portions']))
print()
print('--- DISHES ---')
for l in out: print(l)
print('--- DISH_MEASURES ---')
for l in meas: print(l)
print('--- DISH_NOTES ---')
for l in notes: print(l)
