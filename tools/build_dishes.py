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

out, notes, meas = [], [], []
for d in DISHES:
    out.append(compose(d['name'], d['cat'], d['items'], d['served'], d['key'], ''))
    notes.append("  %s: '%s'," % (d['key'], note(d).replace("'", "\\'")))
    meas.append('%s|%s' % (d['key'], d['portions']))
print()
print('--- DISHES ---')
for l in out: print(l)
print('--- DISH_MEASURES ---')
for l in meas: print(l)
print('--- DISH_NOTES ---')
for l in notes: print(l)
