#!/usr/bin/env python3
"""
Rebuild the food database in index.html from AUSNUT 2023 (FSANZ).

Reads three official workbooks and writes two pipe-delimited blocks:

  FOODS    name | group | kJ | protein | fat | saturated | carbs | sugars |
           fibre | sodium | alcohol | liquid | <23 micronutrients> | food key
  MEASURES key | descriptor:grams ; ...

Foods that exist only in AFCD Release 3 (raw commodities AUSNUT dropped) are
carried over from the previous block untouched, so nothing the app already
knew about disappears.

Basis: AUSNUT publishes everything per 100 g. Foods that FSANZ also measures
by volume (they have at least one measure row carrying a Volume) are converted
to per 100 mL with the food's own specific gravity, which is exactly how FSANZ
derives its own per-100-mL tables.
"""
import openpyxl, re, sys, json

U = '/root/.claude/uploads/2438534a-df17-5a58-8770-38eda2f3d116/'
DETAILS  = U + '467b0eed-AUSNUT2023Fooddetails4.xlsx'
PROFILES = U + '756dcc25-AUSNUT_2023__Food_nutrient_profiles.xlsx'
MEASURES = U + '48e68ebb-AUSNUT_2023__Food_measures.xlsx'

def rows(path, sheet, start):
    ws = openpyxl.load_workbook(path, read_only=True)[sheet]
    for r in ws.iter_rows(min_row=start, values_only=True):
        if r and r[0] is not None:
            yield r

def num(v):
    if v is None or v == '': return 0.0
    try: return float(v)
    except (TypeError, ValueError): return 0.0

# ---- food details: group, specific gravity ---------------------------------
det = {}
for r in rows(DETAILS, 'Food details', 5):
    key = r[2]
    code = str(r[13] or '')
    det[key] = {'name': (r[4] or '').strip(), 'sg': num(r[9]), 'grp': code[:2] or '32'}

# ---- measures: official household portions ---------------------------------
# FSANZ publishes these as gram weights. Foods the app holds per 100 mL get
# their portions in millilitres instead, so a schooner reads as 425 mL and not
# as the 429 g it happens to weigh.
RAW_UNIT = {'millilitres', 'grams', 'gram', 'litre', 'litres', 'kilograms'}
TRAIL_VOL = re.compile(r'[\s,]*\d+(\.\d+)?\s*(ml|mls|litre|l)\b\.?$', re.I)

raw_meas, byvol = {}, set()
for r in rows(MEASURES, 'AUSNUT 2023', 4):
    key, qty = r[1], num(r[4]) or 1.0
    parts = [str(x).strip() for x in r[5:9] if x and str(x).strip() and str(x) != 'None']
    if not parts: continue
    if parts[0].lower() == 'density': continue
    if parts[0].lower() in RAW_UNIT: continue
    grams, vol = num(r[9]), num(r[10])
    if vol: byvol.add(key)
    if not grams: continue
    label = re.sub(r'\s+', ' ', ' '.join(parts))
    label = TRAIL_VOL.sub('', label).strip(' ,')
    if qty != 1: label = ('%g ' % qty) + label
    raw_meas.setdefault(key, []).append((label[:34], grams, vol))

# ---- nutrient profiles -----------------------------------------------------
# columns, by header index in the workbook
C = dict(kj=4, prot=7, fat=8, carb=9, sug=12, fs=14, fib=15, alc=16,
         ca=18, i=19, fe=20, mg=21, ph=22, k=23, se=24, na=25, zn=26,
         va=30, b1=31, b2=32, b3=34, b6=35, fol=39, b12=40, vc=41, vd=46,
         ve=48, sat=49, la=51, ala=52, n3=57, caf=59, chol=60)
MICROS = ['ca','fe','mg','ph','k','zn','se','i','va','vc','vd','ve',
          'b1','b2','b3','fol','b6','b12','chol','caf','n3','la','ala']

def cell(v, k=1.0):
    """Value from the workbook, converted to the per-100-mL basis if the food
       needs it, and rounded back to the precision FSANZ published. Carrying
       more decimals than the source had would only invent accuracy; carrying
       fewer wipes out the micrograms — rounding B12 in milk to a whole number
       zeroes it."""
    if v is None or v == '': return '0'
    try: x = float(v)
    except (TypeError, ValueError): return '0'
    if x == 0: return '0'
    txt = repr(float(v))
    dp = len(txt.split('.')[1].rstrip('0')) if '.' in txt else 0
    x *= k
    a = abs(x)
    dp = min(dp, 0 if a >= 1000 else (1 if a >= 10 else (2 if a >= 1 else 6)))
    out = ('%.*f' % (dp, x)).rstrip('0').rstrip('.') if dp else '%d' % round(x)
    return out or '0'

# Which foods are held per 100 mL rather than per 100 g. A schooner and a
# splash of oil are volumes; sour cream and mayonnaise are spooned, and giving
# them a volume basis would quietly fold their density into every entry as an
# error. So: the food must have a specific gravity (FSANZ leaves it 0 for
# anything it does not measure by volume) and must be something you pour.
LIQUID_GRP = {'11', '29'}          # non-alcoholic and alcoholic beverages
LIQUID_NAME = re.compile(
    r'^(milk|flavoured milk|milkshake|milk shake|smoothie|soy beverage|'
    r'oil,|juice,|water,|coconut water|cordial|stock, liquid|beverage,|drink,)', re.I)

def is_liquid(d, name, key):
    if not d['sg']: return False
    return d['grp'] in LIQUID_GRP or bool(LIQUID_NAME.match(name))

out, seen, kept, liquid_keys = [], set(), set(), set()
for r in rows(PROFILES, 'Food nutrient profiles', 4):
    key = r[1]
    d = det.get(key)
    if not d: continue
    name = (r[3] or d['name']).strip().replace('|', '/')
    liquid = is_liquid(d, name, key)
    k = d['sg'] if liquid else 1.0          # per 100 mL vs per 100 g
    f = [name, d['grp']] + \
        [cell(r[C[n]], k) for n in ('kj','prot','fat','sat','carb','sug','fib','na','alc')] + \
        ['1' if liquid else '0']
    f += [cell(r[C[m]], k) for m in MICROS]
    f.append(key)
    out.append('|'.join(f))
    seen.add(name.lower())
    kept.add(key)
    if liquid: liquid_keys.add(key)

# ---- carry over AFCD-only foods -------------------------------------------
# AUSNUT renames plenty of foods it shares with AFCD, so the two are matched on
# the public food key they both use, not on the name.
AFCD_XLSX = U + '0e33b550-AFCD_Release_3__Nutrient_profiles.xlsx'
afcd_key = {}
for r in rows(AFCD_XLSX, 'All solids & liquids per 100 g', 4):
    afcd_key[(r[3] or '').strip().lower()] = r[0]

# The AFCD-only rows are read from the commit that introduced them, not from
# the working copy, so re-running this after it has already written index.html
# reproduces the same output instead of folding its own output back in.
import subprocess
html = subprocess.run(['git', '-C', '/home/user/Eat-Train', 'show', 'c3f5e14:index.html'],
                      capture_output=True, text=True, check=True).stdout
old = re.search(r'var AFCD = `\n(.*?)\n`;', html, re.S).group(1).split('\n')
carried = []
for line in old:
    p = line.split('|')
    if len(p) < 32: continue
    nm = p[0].strip().lower()
    if nm in seen or afcd_key.get(nm) in det: continue
    # old rows carry 20 micros; pad the three new ones with 0 and no key
    carried.append('|'.join(p[:32] + ['0', '0', '0', afcd_key.get(nm, '')]))

foods = out + carried
mlines = []
for k, v in raw_meas.items():
    if k not in kept: continue
    sg = det[k]['sg'] if k in liquid_keys else 0
    # Two vessels of the same size are the same portion, so the amount is what
    # gets deduplicated, not the word in front of it.
    seen_amt, picks = set(), []
    for label, grams, vol in v:
        amt = round((vol or (grams / sg)) if sg else grams, 1)
        if not amt or amt in seen_amt: continue
        seen_amt.add(amt)
        picks.append((label, ('%g' % amt)))
    picks.sort(key=lambda x: float(x[1]))
    if picks:
        mlines.append('%s|%s' % (k, ';'.join('%s:%s' % (l, a) for l, a in picks[:6])))

# ---- write both blocks back into the page ---------------------------------
page = '/home/user/Eat-Train/index.html'
cur = open(page, encoding='utf-8').read()
cur = re.sub(r'var FOODS = `\n.*?\n`;',
             lambda m: 'var FOODS = `\n' + '\n'.join(foods) + '\n`;', cur, count=1, flags=re.S)
cur = re.sub(r'var MEASURES = `\n.*?\n`;',
             lambda m: 'var MEASURES = `\n' + '\n'.join(mlines) + '\n`;', cur, count=1, flags=re.S)
open(page, 'w', encoding='utf-8').write(cur)
print('AUSNUT foods %d · carried from AFCD %d · total %d' % (len(out), len(carried), len(foods)))
print('liquids %d · foods with official portions %d' % (sum(1 for l in foods if l.split('|')[11] == '1'), len(mlines)))
print('foods block %.0f KB · measures block %.0f KB · index.html %.0f KB' %
      (len('\n'.join(foods)) / 1024, len('\n'.join(mlines)) / 1024, len(cur) / 1024))
