# Eat & Train

A calorie and training tracker in a single HTML file, built on the **Australian Food
Composition Database, Release 3** (FSANZ). No build step, no server, no account —
open `index.html` and it works, including with no signal.

## What it does

Four tabs, ordered by how often you actually use them.

- **Today** — the log. Energy budget, the weekly check-in when one is due, a weigh-in
  prompt until you have, macros, vitamins and minerals, meals and training.
- **Train** — one card, one session: Run, Workout, Other or Lift. Plus steps.
- **Progress** — where you go to review: the coach check-in and its evidence, measured
  expenditure, 14-day energy, weight trend, composition, weekly averages, and the
  weigh-in form with its history.
- **Me** — who you are and how the maths is set up: account, markers, composition,
  resting-rate model, daily activity, coach and goal, and the resulting numbers.

**Foods & recipes** is not a tab. You never set out to visit a food library — you hit
it mid-flow when something is missing, so it lives behind a glyph in the header, and
every search result list ends with *"Not there? Scan or add it"*. That is the moment
you find out, so that is where the offer belongs.

## The food data

Every value comes straight from the official AFCD Release 3 nutrient profiles:

- Solids are per 100 g.
- The 213 foods FSANZ also publishes as liquids are held **per 100 mL** from that
  sheet, which is the right basis for a drink — a schooner is 425 mL, not 425 g.
- Energy is the label figure, *energy with dietary fibre, equated*.
- Foods keep their AFCD classification, which drives the category filters.

FSANZ publishes 213 of those foods per 100 mL as well. Only the 120 that are actually
poured or drunk use that basis — yoghurt, custard and sauces stay per 100 g, because
they are eaten by the spoon and mixing the two bases would silently fold their density
into every entry as a few percent of error.

## Portions

AFCD ships nutrients per 100 g and no serve sizes, so portions are a layer on top: a
rule table matched against the AFCD name, giving typical Australian household measures
— a slice of sourdough at 50 g, a schooner at 425 mL, a rasher of bacon at 25 g, a
tub of yoghurt at 170 g. Pick the portion, say how many, and the grams follow.

Anything the rules do not match falls back to the **Australian Dietary Guidelines**
standard serve for its category: 75 g of vegetables, 150 g of fruit, 65 g of cooked
meat. Every food also keeps a plain 100 g option and free gram entry, so nothing is
ever un-loggable.

These weights are typical, not official — a real slice varies with the loaf. If FSANZ
publishes a measures file alongside the nutrient profiles, its weights would be worth
using in place of these.

Search is built for the gap between how AFCD writes names and how people type them.
AFCD says "Nut, almond" and "Bread, from white flour, sour dough"; you can type
"almonds" and "sourdough". Each term is tried verbatim, then singularised, then with
spacing and punctuation stripped, each fallback ranked below the last. A small synonym
table covers the rest — yogurt, snags, roo, avo, chook, spuds, fries, cookie.

### Supermarket products

AFCD covers generic foods, not the branded lines on a Coles or Woolworths shelf. Two
ways to add those:

- **One item** — copy its Nutrition Information Panel into **New food**. The panel on
  the box is more authoritative than any database.
- **A whole list** — [Open Food Facts](https://au.openfoodfacts.org/) is the open,
  barcode-level product database, ODbL licensed. Filter its advanced search by brand
  or country, download the result as CSV, and load it under **Supermarket products**.

### Barcode scanning

**New food** takes a barcode. Scan it with the camera and the panel is pulled from Open
Food Facts and dropped into the form to check against the pack before saving; type it
instead if you prefer, and an unknown barcode is kept with whatever you type so the
product is there next time.

`BarcodeDetector` is native in Chrome and Edge and used where it exists. It is absent
from every browser on iOS — they are all WebKit underneath — so relying on it would
mean a scanner that silently does nothing on an iPhone. The fallback decodes EAN-13 and
UPC-A from the camera frame directly: threshold each row at the midpoint of its own
darkest and lightest pixels, find the guard patterns, sample the centre of all 95
modules, decode the left six by L/G parity to recover the thirteenth digit, and verify
the checksum. Only the guide box is analysed, blown up, so a barcode filling it lands on
enough pixels per module.

That keeps the app free of a WebAssembly dependency it could not load offline anyway.
It is tested against generated codes at several scales, upside down, with noise, and
against random bars to confirm it does not invent a result. It will not match a
dedicated scanning library on a creased or curved pack.

Scanning needs camera permission and a secure origin, so it works from GitHub Pages and
not from a local file opened with `file://`.

### Live lookup

The app can also query Open Food Facts directly, which is off by default. Switched on
under **Supermarket products**, the search sheet offers a button to look up whatever
you typed — one request, on your tap, carrying the search text and nothing else. No
account, no identifier, no history. A query of 8–14 digits is treated as a barcode and
goes straight to the product endpoint. Anything you pick is written to this device, so
the same product never needs a second request.

Built to their published API rules:

- **Product reads use v3**, the current version; v2 is deprecated and kept only as a
  fallback. Barcodes go straight to the product endpoint.
- **Full-text search does not exist in v2 or v3.** Only Search-a-licious and the legacy
  CGI path offer it. Search-a-licious defines both `POST /search` and `GET /search`,
  allows any origin with `OPTIONS`, and takes `q`, `page_size`, `page`, `fields`,
  `sort_by`. Its parameter model sets `extra="forbid"`, so an invented parameter name
  is a hard 422 rather than something quietly ignored. Responses carry `hits`, and its
  Open Food Facts index holds exactly the nutriments this app reads.
- Whichever route answers is remembered and tried first next time, so falling through
  several shapes costs extra requests once rather than on every search.
- **Rate limits are 10 searches and 15 product reads per minute per IP**, enforced with
  IP bans. Lookups are one deliberate tap — never as you type, which their docs single
  out as the fastest way to get blocked — and a client-side cap of 8 searches a minute
  sits under their limit. HTTP 429 and 503 get their own messages rather than a generic
  failure.
- Product data is used under the **Open Database License**, credited in the app.

One rule cannot be honoured from a static page: they ask for a custom `User-Agent`
identifying the app, and browsers forbid scripts from setting that header. Routing
lookups through a small server-side proxy would fix it, and would centralise rate
limiting at the same time.

This is the one place the app touches the network, and it needs the page to reach
another origin. The file on your phone can; the claude.ai artifact preview cannot,
because artifacts run under a CSP permitting no external hosts. There the lookup fails
with a message saying so, and everything else works unchanged.

### Bulk import

The importer is built for that export specifically. It sniffs tab vs comma separators,
prefers `_100g` columns over `_serving` decoys, converts sodium from grams to
milligrams, derives sodium from `salt_100g` when a row has no sodium of its own
(1 g salt = 400 mg sodium), prefixes the brand onto the product name, and drops blank
and duplicate rows. Imports land in their own **Packaged** category so FSANZ-sourced
numbers stay visually distinct from crowd-sourced ones.

Open Food Facts is crowd-sourced: coverage is patchy and entries are occasionally
wrong. Treat it as a convenience layer over AFCD, not a replacement.

The [FoodSwitch database](https://www.georgeinstitute.org/our-research/areas/food-policy/foodswitch-data-on-the-worlds-packaged-foods)
from The George Institute is the better Australian packaged-food source — built from
in-store audits at Coles, Woolworths, ALDI and IGA — but it is available by research
request rather than open download.

## Running

Two modes. **Run** is a duration and a pace you type, with optional elevation gain and
strides. **Workout** opens the structured plan, laid out the way a session is written:

    Warm up      minutes @ pace
    Interval     distance or time × reps @ pace
    Between      rest · jog · float · compromised
    Cool down    minutes @ pace

Distance-or-time is a toggle, so `6 × 1 km @ 3:30` and `6 × 5 min @ 4:05` are the same
form. Compromised sessions put a strength or plyometric effort between reps instead of
a recovery, priced by MET for its duration. Every field is remembered per mode.

### Energy

Running uses the **ACSM metabolic equations** rather than a MET value, because a MET
bin cannot tell a 3:30 kilometre from a 5:30 one and cannot price a hill at all:

    running  net VO₂ = 0.2·v + 0.9·v·grade     (mL/kg/min, v in m/min)
    walking  net VO₂ = 0.1·v + 1.8·v·grade
    5 kcal per litre of O₂

Applied per block, so a warm up, a rep and a float are each costed at their own pace.
Everything is net of resting metabolism, which your baseline already covers.

This falls out at roughly **1 kcal per kg per km, near enough regardless of pace** —
the long-standing finding that the energy cost of running a kilometre is close to
speed-independent on the flat. Pace changes how long you are out there far more than
it changes what a kilometre costs. Elevation is where a session really departs from
that, which is why gain is an input.

A compromised block takes the shape you actually use: seconds per set, **sets per gap**,
and an optional **walk after each set**. Two 40-second carries with a 20-second walk
after each is `40` sec × `2` sets, walk `20`. The sets are paused-belt time and earn no
distance; the walks run on the belt and do.

Both modes take an optional **recorded distance and time**. A plan only accounts
for the running it describes — jogging between rep starts, drills, and ground covered
during a loaded carry are all real distance it cannot see. Whatever the device recorded beyond
what the plan describes becomes its own block, priced at the pace those leftover
minutes and kilometres imply — walking if that is what it works out to, standing if no
ground was covered. When the plan describes *more* than was recorded, that is reported
rather than quietly corrected, because a stated discrepancy is more use than a silent
adjustment when the protocol varies session to session.

Afterburn (EPOC) is an optional flat 6%, off by default. It is real after hard
sessions but too variable to state precisely, so it is a labelled choice rather than
something folded silently into the number.

### Steps

A watch counts every step, training included, and the session is already priced in
full — so counting both pays for the run twice. Steps taken during logged sessions are
estimated from cadence and taken back out of the daily total; only what is left is
added. On an hour-long run that correction is worth over a thousand kilojoules.

Cadence sets the estimate and is adjustable. The figure is stored with the session when
you log it, so changing cadence later does not rewrite your history.

## Moving food between meals

Press and hold a logged item to lift it, then drag it to another meal — the target
highlights and a line shows where it will land, including the position within that
meal. A short swipe still scrolls the list, so the gesture only takes over once the
long press completes.

This is built on pointer events rather than HTML5 drag-and-drop, which never fires on
touch devices. Every row also carries a move button that opens a meal picker, so
dragging is never the only way to do it.

## Vitamins and minerals

Eighteen nutrients tracked against the **Nutrient Reference Values for Australia and
New Zealand** (NHMRC), read from your sex and age: calcium, iron, magnesium,
phosphorus, potassium, zinc, selenium, iodine, sodium, vitamins A, C, D, E, thiamin,
riboflavin, niacin, folate, B6 and B12. Cholesterol and caffeine are tracked without
targets, since Australia sets none.

Each nutrient is read against two numbers at once. The bar runs from zero to the
**Upper Level**, with a tick marking the **RDI**, so short of target, in range, and
over the limit are one glance apart. Tap through for amounts, both reference figures,
and which foods actually delivered each nutrient that day — the useful half of a
shortfall is knowing what to eat more of.

Two honesty notes:

- AFCD populates every nutrient for every food, so a low total is a real shortfall
  rather than a gap in the data. It still only counts what you logged, and knows
  nothing about supplements.
- Several Upper Levels were written for a supplement form, not for food: magnesium's
  applies to supplements, niacin's to nicotinic acid, folate's to folic acid, vitamin
  A's to preformed retinol, B6's to supplemental pyridoxine, vitamin E's to
  alpha-tocopherol. Those are shown for reference but never flagged as exceeded,
  because passing them on diet alone does not mean what the number suggests.

## Coach

A tracker that measures your expenditure but never acts on it leaves the useful half
undone. Switched on under **Me**, once a week the app compares your trend rate against
the rate your goal implies and moves the target by the difference, priced at 32,200 kJ
per kilogram of body mass. Changes are capped at 8%, floored at resting rate, and each
one is kept with the rate and coverage that produced it.

It refuses to adjust on a week you did not log. Below 70% coverage it says so and
changes nothing — fitting a target to a half-recorded week is fitting the gaps. The
coached number is a **rest-day base**; the day's own training is still added on top.

### Trend weight

A scale reading is body mass plus water, gut contents and yesterday. Every calculation
— resting rate, macro targets, run and step energy — runs on an exponentially weighted
average with a ten-day half-life rather than the last reading, so a dehydrated
post-run weigh-in does not rewrite the day. The half-life is expressed in days, so a
gap between weigh-ins is weighted correctly instead of counting as a single step.

### Fuel around training

Training energy already lifts a session day, and carbs absorb all of it because protein
and fat are fixed per kilogram. **Even** leaves it there. **Moderate** and **Strong**
add the other half: rest days give some back so session days get more, with the factors
normalised to a mean of one so the week lands where it started. On a runner's week,
Moderate moves a rest day from 304 to 181 g of carbs and a long-run day from 679 to
887 g.

## Recipes

The easiest recipe builder is a meal you already logged — the ingredients and amounts
are sitting there. Tap the save icon on any meal, name it, say how many servings it
makes, and it becomes a single food whose portion is one serving. Everything downstream
works unchanged, micronutrients included: log one serving of a two-serve batch and you
get exactly half of what went in.

## How the energy maths works

**Resting metabolic rate.** Three models, and the app uses the best one your inputs
support. You can also force one.

| Model | Needs | What it does |
|---|---|---|
| Mifflin-St Jeor | height, weight, age, sex | The best-validated equation with no body composition. Within roughly 10% for most people. |
| Katch-McArdle | + body fat % | `370 + 21.6 × lean mass`. Better when you are lean or muscular, because it stops guessing your composition. |
| Tissue-level | + skeletal muscle mass | Burns each tissue at its own rate: muscle 13, fat 4.5, liver 200, brain 240, heart and kidneys 440 kcal/kg/day (Elia 1992; Wang 2010). Organ mass scales with body surface area; brain does not, being near-constant in adults. |

**Daily expenditure.** `RMR × your non-exercise activity multiplier`, then logged
sessions are added on top. The multiplier deliberately describes your day *excluding*
training, which is what stops workouts being counted twice.

**Training.** `(MET − 1) × 3.5 × kg / 200 × minutes`, in kcal, converted to kJ. The
`− 1` removes the resting cost of that hour, which your baseline already covers.

**Measured expenditure.** Once you have about ten logged days and three weigh-ins
spread over ten days, the app stops predicting and starts measuring: average intake,
adjusted by the least-squares trend in your weight at 32,200 kJ per kg of body mass.
This beats every equation, and you can switch your targets over to it.

**Bone density and body water** are tracked and charted, never computed with. Bone
tissue burns about 2.3 kcal/kg/day — a whole skeleton is under 30 kJ a day, which is
far inside the noise of any of the models above.

A note on inputs: bioimpedance scales like the Garmin Index S2 carry real error on
body fat (several percentage points against DEXA) and drift with hydration. Read them
as trends over weeks, not as measurements. That is also why measured expenditure is
worth switching to as soon as it is available.

## Running it on your phone

1. Put `index.html` somewhere your phone can reach it — AirDrop or email it to
   yourself, or serve the folder over HTTPS.
2. Open it in Safari or Chrome.
3. Share → **Add to Home Screen**.

It then launches full screen and runs with no network. Fonts come from Google Fonts
when online and fall back cleanly when not.

## Sync

Data lives on this device first and always. Sign in from the Me tab and it is
also kept on Supabase, so a new phone or a laptop picks up where you left off.

Sign-in is a six-digit code emailed to you — no password to invent, lose or reuse.

Sync is a **two-way merge, per row, newest wins**. A day edited on the phone and a
different day edited on the laptop both survive; the same day edited on both keeps the
later one. Days, weigh-ins and your own foods are each their own row, so a conflict is
scoped to the thing that actually conflicts rather than the whole history. Bulk CSV
imports stay local — they are a convenience cache, not your data, and thousands of rows
do not belong on a server.

Every table is protected by row-level security keyed to the signed-in user. The
publishable key in the source is meant to be public; RLS is what makes that safe. The
`anon` role can neither read nor write any of it — verified, not assumed.

Sync needs the page to reach Supabase, so like the Open Food Facts lookup it works from
GitHub Pages or the saved file, and not in the claude.ai artifact preview.

## Your data

Everything is kept in that browser's local storage on that device. Nothing is sent
anywhere and there is no account. Clearing site data erases it, so use **Copy backup**
under the database icon and keep the JSON somewhere safe.

## Editing it

One file, no dependencies. The food table is a pipe-delimited block near the top of
the `<script>`:

```
name | AFCD group | kJ | protein | fat | saturated | carbs | sugars | fibre | sodium mg | alcohol g | liquid
```

Activities and their MET values sit just below it in `ACTIVITIES`.

## Source

Food Standards Australia New Zealand, *Australian Food Composition Database — Release 3*.
<https://www.foodstandards.gov.au/science-data/food-nutrient-databases/afcd/data-files>
