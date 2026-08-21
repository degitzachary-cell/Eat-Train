# TrueCount

Every kilojoule, honestly kept. A calorie and training tracker in a single HTML file, built on **AUSNUT 2023** and the
**Australian Food Composition Database, Release 3** (FSANZ). No build step, no server,
no account — open `index.html` and it works, including with no signal.

## On a phone

Open it in Safari or Chrome and use **Add to Home Screen**. It installs as a standalone
app — its own icon, no browser chrome, the dark status bar — because `manifest.webmanifest`
and the PNG icons sit next to `index.html`.

Those icons have to be real files. iOS ignores an SVG `apple-touch-icon`, and ignores a
`data:` URI in one too, and quietly falls back to a screenshot of the page instead. The
SVG favicon in the head still does the browser tab, where it stays sharp at any size.

The mark is redrawn rather than scaled for the icon: a 1.5px ring on a 96-unit canvas is
under two device pixels at 180px. Same forms, heavier strokes, and pulled in to 72% so it
survives both iOS's corner rounding and Android's maskable crop.

## Look

Forest green and champagne, set in Hanken Grotesk with Newsreader for numbers and
headings. One palette, not two: the scheme is built dark, and a light translation of it
would be a different design rather than the same one inverted, so there is no light mode
and no `prefers-color-scheme` block.

Everything visual resolves through the twenty-odd custom properties in `:root` — every
rule and every `var()` in the script points at them, so a restyle happens there rather
than in four hundred places. Bars are 3px and square, filled `--ink` for macros and gold
for fibre; micronutrients use their own status scale instead, since gold and off-white
say nothing about whether you are short of iron. Sections are hairlines rather than
cards, and the only elevated surfaces left are the sheets.

## What it does

Five tabs, ordered by how often you actually use them. Where a tab runs long it splits
into sub-sections rather than a three-storey scroll — and where it does not, it is left
alone, because a diary is meant to scroll.

- **Today** — the log. Energy budget, the weekly check-in when one is due, a weigh-in
  prompt until you have, macros, vitamins and minerals, meals and training.
- **Train** — one card, one session: Run, Workout, Other or Lift. Plus steps.
- **Recipes** — what to cook, opening on what fits what is left of today.
- **Progress** — where you go to review: the coach check-in and its evidence, measured
  expenditure, 14-day energy, weight trend, composition, weekly averages, and the
  weigh-in form with its history.
- **Me** — who you are and how the maths is set up: account, markers, composition,
  resting-rate model, daily activity, coach and goal, and the resulting numbers — always
  for today, not for whichever day the diary happens to be showing.

**The food database** is not a tab. You never set out to visit a food library — you hit
it mid-flow when something is missing, so it lives behind a glyph in the header, and
every search result list ends with *"Not there? Scan or add it"*. That is the moment
you find out, so that is where the offer belongs. Recipes used to live there too, which
was the wrong shelf: choosing dinner is a thing you set out to do.

## First run

The app cannot say anything useful without a body, and until now its defaults were
mine — anyone else opening it got a 32-year-old, 178 cm, 82 kg male and a set of
numbers that looked authoritative and belonged to someone else. Setup asks instead,
and will not hand over a number until it has enough to compute one honestly.

Four screens. **You** takes sex, age, height and weight, and nothing continues until
all four are in — sex and age also pick the Australian NRV band for the vitamin and
mineral targets, which differ by both. **Scale numbers** takes body fat, muscle mass
and bone mass off a Garmin Index S2 or similar, all optional and openly skippable,
because an invented body-fat number is worse than none. **Your day** takes the
non-exercise activity level and the goal. Then it shows you the answer: resting rate,
baseline expenditure, today's target, and which of the three models produced it —
tissue-level if you gave it the scale numbers, Katch-McArdle on body fat alone,
Mifflin-St Jeor otherwise.

The weight typed during setup is also recorded as the first weigh-in, so the trend
line and the charts have something to start from rather than opening empty.

**An account stays optional.** Everything works from this browser alone, offline,
indefinitely. Signing in is offered first only so that someone arriving on a second
phone is not made to re-enter a body the server is already holding — and if they pick
it, setup closes as soon as the sync brings that body back. Every screen that offers
sign-in also offers a way past it.

Nothing is written to the profile until every required answer is in, so abandoning
setup halfway leaves no half-built body behind. Anyone with a diary saved before this
existed is not sent through it.

## The food data

**4,127 foods**, every value straight from the official FSANZ workbooks.

The base is **AUSNUT 2023**, the survey database: 3,741 foods, and unlike AFCD it does
not stop at raw commodities. Lasagne, pad thai, a Big Mac, a flat white with reduced-fat
milk, sushi, a fun-size packet of Maltesers — the things people actually eat and
therefore actually log. The **386 AFCD Release 3 foods AUSNUT has no entry for** are
carried over unchanged, so nothing the app already knew about was lost. The two are
matched on the public food key they share, not on the name, because AUSNUT renames a
good deal of what it inherits.

- Solids are per 100 g.
- The **348 foods FSANZ measures by volume** — drinks, milks, oils, stock — are held
  **per 100 mL**, which is the right basis for a drink: a schooner is 425 mL, not 425 g.
  The conversion uses each food's own specific gravity, which is how FSANZ derives its
  own per-100-mL tables.
- Sour cream, yoghurt, custard and mayonnaise stay per 100 g even though FSANZ gives
  them a density. They are eaten by the spoon, and putting them on a volume basis would
  silently fold their density into every entry as a few percent of error. The test is
  whether FSANZ records a specific gravity *and* the food is something you pour.
- Energy is the label figure, *energy with dietary fibre*.
- Foods keep their AUSNUT major group, which drives the category filters. Group 13 is
  *cereal based products and dishes* — bread, pasta dishes, pizza, sushi, sandwiches —
  so it is filed as **Grain dishes**, not Baked goods.

AUSNUT also carries three fats AFCD did not: long-chain omega-3 (EPA + DPA + DHA),
linoleic acid and alpha-linolenic acid. All three are tracked alongside the other
twenty micronutrients, against the NHMRC Adequate Intakes. The 386 carried-over AFCD
foods sit at zero for those three, which is the only honest value available for them.

## Portions

Portions come from **AUSNUT 2023 Food measures** — the household measures the national
survey actually used, and their weights. **2,604 of the 4,127 foods** have them: a
regular slice of white bread at 33 g, a thick Abbott's Village slice at 45 g, a small
wrap at 36 g, a McDonald's Big Mac at 214 g, one Malteser at 2.5 g. Two vessels of the
same size collapse to one entry, since a 330 mL can and a 330 mL bottle are the same
portion. Liquids are offered in millilitres to match their basis, so a beer reads as a
330 mL can rather than the 333 g it weighs.

Behind those sits the original rule table, matched against the food name, for the 1,523
foods FSANZ has no measures for and for the local sizes it never recorded — AUSNUT has
no schooner, middy or pint. Where both apply the FSANZ weight comes first and the rule
is dropped if it lands within 8% of it, so beer offers can, bottle, schooner, middy and
pint without offering the same volume twice.

Anything neither covers falls back to the **Australian Dietary Guidelines** standard
serve for its category: 75 g of vegetables, 150 g of fruit, 65 g of cooked meat. Every
food also keeps a plain 100 g option and free gram entry, so nothing is ever
un-loggable.

Search is built for the gap between how FSANZ writes names and how people type them.
It says "Nut, almond" and "Bread, from white flour, sour dough"; you can type
"almonds" and "sourdough". Each term is tried verbatim, then singularised, then with
spacing and punctuation stripped, each fallback ranked below the last. A small synonym
table covers the rest — yogurt, snags, roo, avo, chook, spuds, fries, cookie.

### Supermarket products

AUSNUT covers named products where the survey met them, but not the whole branded
shelf at Coles or Woolworths. Two ways to add the rest:

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
from every browser on iOS — they are all WebKit underneath — so relying on it would mean
a scanner that silently does nothing on an iPhone. Everything below is the fallback that
runs there, and it keeps the app free of a WebAssembly dependency it could not load
offline anyway.

**It reads run lengths, not a fixed grid.** The first version took the leftmost and
rightmost dark pixel in a row, assumed everything between them was ninety-five modules of
barcode and sampled the middle of each one. That is only true of a photograph of nothing
but a barcode. A printed word, the edge of the pack, a shadow, the human-readable digits
under the bars or the next product on the shelf moved one of those two endpoints, and
every module after it was read off the wrong place. It also had to be told the scale, so
a barcode that did not fill the box failed.

Each digit is four alternating runs totalling seven modules, so a digit can be recognised
by the *ratios* between its four widths. Those are the same whether the barcode fills the
box or a third of it, and they survive the blur that turns a crisp edge into a ramp.
Nothing outside the guard patterns has to be barcode at all: the decoder looks for a
start guard anywhere in the row and walks on from there.

Three readings are tried, in order of how much they assume:

1. **Run widths from a found guard** — the main path, and the one that copes with
   clutter in the box.
2. **A grid laid from that same guard**, at a spread of scales and a pixel either side.
   On a soft picture a one-module bar blurred over four pixels has no edges left to
   measure: its width is gone, but its position is not.
3. **A grid laid between the row's dark extremes** — the old method, kept as a last
   resort. Every row gets both better readings before any row gets this one, so a guessed
   span cannot beat a properly located barcode further down the frame.

**Thresholding is Otsu's, per row.** A row crossing a barcode has two clear peaks, ink
and paper, and Otsu finds the split between them — which copes with a torch on one side
of the pack where a fixed threshold, or the midpoint between the darkest and lightest
pixel, does not. The threshold taken is the midpoint between the two class means rather
than the bin Otsu stopped at, because on a clean black-on-white row that bin is zero and
a threshold of zero puts every pixel on the same side of it.

Rows are read middle-out, thirty-three of them, forwards and reversed so the pack can be
upside down. The guide box is analysed alone and squashed to 1024 × 256 — a barcode is
the same all the way down, so trading height for width spends the pixels where the
information is.

**What it will and will not believe.** A located EAN-13 is accepted on one row: twelve
digits each had to match their pattern and then agree with a check digit. Two things are
not accepted that easily and must turn up on a second row first — a guessed span, because
the span was a guess, and any EAN-8, because seven digits and a one-in-ten check is thin
evidence. EAN-8 additionally has to show both quiet zones, which a field of evenly spaced
stripes does not have. On top of all that the live scanner requires two consecutive frames
to agree before it acts.

It is tested against generated codes at several scales, upside down, tilted, out of focus,
under glare, on a grey pack, with sensor noise, with the printed digits and the pack edge
and a neighbouring barcode in the box, with the quiet zone clipped, and as EAN-8 — 22 of
23 cases, against 16 for the version it replaces. The one it still fails is a four-pixel
blur on a six-pixel module, which is a picture with no barcode left in it; the same blur
on a barcode held closer reads fine.

Against 500 frames of deliberately barcode-like random stripes it returns a code about
once. That floor is not removable: a random pattern that satisfies every digit table and
the check digit *is* a valid barcode as far as any decoder can tell. Real scenes do not
look like that, and the two-frame rule covers the rest.

**Camera.** It asks for 1920 × 1080 and continuous focus, because more pixels across the
barcode is the single biggest thing that makes a scan work and phones default to a focus
that never settles on something this close. Where the camera reports a torch, a button
appears over the preview — a dim pantry is the other half of why scanning fails. Frames
are read fifteen times a second; a frame takes longer than that to change meaningfully,
and the spare time keeps the preview smooth.

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
wrong. Treat it as a convenience layer over the FSANZ data, not a replacement.

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

Twenty-two nutrients tracked against the **Nutrient Reference Values for Australia and
New Zealand** (NHMRC), read from your sex and age: calcium, iron, magnesium, phosphorus,
potassium, zinc, selenium, iodine, sodium, vitamins A, C, D, E, thiamin, riboflavin,
niacin, folate, B6 and B12, plus long-chain omega-3, linoleic and alpha-linolenic acid.
Cholesterol and caffeine are tracked without targets, since Australia sets none.

**Free sugars** and **trans fat** sit with the macros rather than in this list, because
the guidelines write them as a share of energy the way saturated fat is written: under
10% for free sugars (Australian Dietary Guidelines, and the WHO's figure), under 1% for
trans fat (NHMRC). Both move with the day's target. Free sugars rather than total sugars,
because the sugar in an apple and the sugar in a soft drink are the same molecule and a
different problem, and the guideline is written about one of them.

### Why not more of them

Because AUSNUT does not have more. It carries **exactly nine minerals**, all nine of
which are here. There is no copper, manganese, chromium, molybdenum or fluoride in it,
and no vitamin K, biotin, pantothenic acid or choline either — nutrients that have
Australian reference values but no Australian food data behind them. Adding them would
mean importing USDA FoodData Central and matching American foods to Australian ones,
which trades the thing this app is built on for a longer list. Its "other components"
section is three items — caffeine, cholesterol and tryptophan — and the only one not
tracked is tryptophan, which is useful as a niacin precursor that FSANZ has already
folded into the niacin equivalents figure used here.

Each nutrient is read against two numbers at once. The bar runs from zero to the
**Upper Level**, with a tick marking the **RDI**, so short of target, in range, and
over the limit are one glance apart. Tap through for amounts, both reference figures,
and which foods actually delivered each nutrient that day — the useful half of a
shortfall is knowing what to eat more of.

Two honesty notes:

- FSANZ populates every nutrient for every food, so a low total is a real shortfall
  rather than a gap in the data. It still only counts what you logged, and knows
  nothing about supplements.
- Several Upper Levels were written for a supplement form, not for food: magnesium's
  applies to supplements, niacin's to nicotinic acid, B6's to supplemental pyridoxine,
  vitamin E's to alpha-tocopherol. Those are shown for reference but never flagged as
  exceeded, because passing them on diet alone does not mean what the number suggests.
- **Vitamin A and folate used to be in that list and no longer are.** Their limits are
  written against preformed retinol and folic acid, and AUSNUT reports both of those on
  their own — 1,779 foods carry retinol, 470 carry folic acid. So the RDI is still read
  against retinol equivalents and dietary folate equivalents, which is what the RDI is
  for, while the limit is checked against the form the limit was actually set for. Eat
  250 g of lamb's liver and the app now says so: 78,500 µg of preformed retinol against
  a 3,000 µg ceiling. It also says how much of the day's total is that form, so the flag
  is never arbitrary.

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

### The tab

Recipes get their own tab, and it is a section you browse rather than a library you
search. You come here to be shown something worth cooking, look at it, and decide — the
deciding is the whole point, so the tab is pictures and headlines rather than rows and
numbers. Open one to read the method, log a serve to a meal, and you land in your log
with it sitting there.

**For today** is the top of the tab, and it answers the day you are actually having: one
hero card and two beside it, ranked on how much of the remaining energy a serve fills,
how much of the outstanding protein and fibre it brings, and which of the micronutrients
you have been short on all week it happens to deliver. Each card says why it is there —
*31% of what is left · +56 g protein · +9.2 g fibre*. Overshooting is priced rather than
disqualifying, because a 3,000 kJ dinner with 400 kJ left is wrong and a 2,000 kJ one is
merely a big night. The micronutrient half reads the **last seven logged days**, not
today: a shortfall you have been carrying all week is worth more than one you have had
since breakfast.

Recipes are still ordinary foods underneath, so they also come up in the normal food
search when you are logging, filed under a **Recipes** category. That path logs a serve
as written; the tab is where the variations and the method live.

**Browse** is everything else, under meal chips — breakfast, lunch, dinner, snacks.
Reach for a chip and the suggestions get out of the way, because you have just said what
you are after. Whatever is suggested is not repeated below it either; printing the same
card twice costs half the screen and says nothing the first one did not. A recipe you
save yourself is filed under the meal you saved it from, and one with no meal recorded
at all shows under every chip rather than under none.

### Pictures

Every recipe has a picture slot, and a recipe carries its own image as a field. Until
there is a photograph in it, the slot draws the dish's **base** — a bowl of rice, a plate
of pasta, a fried egg — as line art on a wash tilted by the recipe's own name, so a grid
of them does not tile. That is a picture the file can carry offline, which a URL to
somebody's CDN is not, and it is a great deal better than a grey rectangle apologising
for the photograph that is not there.

An image is held the way everything else here is: in the file, as a data URI. It costs
what it costs — budget for it, because the app is one download and there is nowhere for
a lazy second request to come from when you are cooking with no signal.

### What ships is not yours to lose

The seven recipes are part of the app. They are checked on every load and on every sync
pull, and anything missing goes back — matched on a key each carries rather than on its
name, so renaming one or rewriting its ingredients keeps your version. There is no delete
on them, because one stray tap should not take something out of the app. Edit them all
you like; your changes are kept and synced.

An install that predates the key adopts it rather than gaining a second copy of a recipe
already in the list.

### A partner's shelf

A recipe can carry a **source**. When it does, it wears that name as a badge on its card
and its dishes group into their own section under Browse rather than being shuffled in
among your own — a meal prep company's range is a shelf, not a dozen strangers in your
recipe box. Suggestions ignore the distinction: if a partner's dish is the thing that
fits tonight, it is the thing that fits tonight.

Nothing ships with a source set. The field, the badge, the grouping and the pipeline that
carries them are all in place, so a range drops in as data.

### The starter set

Seven recipes ship with the app, written rather than scraped — the FSANZ mixed dishes
are survey averages, not something anyone cooks. Pad grapao, caramelised onion pasta
with paprika chicken, dan dan mian, a protein yoghurt bowl, a chicken breast wrap, a
chicken garden salad, and eggs and salmon on rye. Each carries a cuisine, a base, a
time, the meals it suits, its ingredients, and its method.

**Every one is written for two.** Cooking for one means weighing out half of everything
and the second serve is where lunch tomorrow comes from; the app already halves the
nutrition per serving either way.

They are seeded once, on first load, and are ordinary recipes afterwards — editable,
deletable, and not re-added if you throw them away.

Their nutrition is not taken on trust from whoever wrote them. Every ingredient is
resolved to an AUSNUT food key and the totals are computed from the database, then
checked against the per-serve figures the recipe claims. All seven land within 15% on
energy and five within 8%, which is about as close as a hand-written recipe and a
national food composition table ever agree.

### Variations

Each recipe carries up to five one-tap variations: **less carbs**, **more carbs**,
**more protein**, **more fibre**, and one micronutrient the dish is well placed to
deliver — iron, calcium or omega-3. A variation is a set of amount changes and
additions, not a second recipe: more protein on the pad grapao takes the chicken from
360 g to 440 g, lifts the sauce by half so it does not taste thin, and adds a fried egg.

Tap a card and the recipe opens the way you would use it: the tags, the variation chips,
per-serve energy and macros that move as you switch between them, the micronutrients it
is strong in, the ingredient list at the amounts that variation implies, and the method.
Log a serve from there and the entry records which variation you cooked — `Pad grapao ·
more protein` — carrying that variation's thirteen ingredients, while the recipe itself
keeps its own twelve untouched. Editing the recipe and deleting it live at the bottom of
that same view, with the recipe, rather than as icons on the shelf you were browsing.

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

### Editing what you cooked

A recipe's nutrition is **derived from its ingredients, never stored**. The totals
recorded at save time survive only as a fallback for an ingredient that can no longer be
found. That is what lets an edit take effect everywhere at once, and it is why a recipe
written before the AUSNUT rebuild does not quietly keep reporting the old database's
numbers — or carry hard zeros for omega-3, linoleic and alpha-linolenic acid, which had
no keys when it was saved.

Ingredients are held by **public food key** first and by name only as a fallback, since
names move between releases. Recipes saved before keys existed get them backfilled once,
on load.

A logged recipe is one row in the diary, and that row **remembers what went into it**.
Tap the list icon on it to open the ingredients: change a weight, drop something,
and the entry recomputes — for that day only. The recipe keeps its own amounts. Editing
the recipe from the food library does the opposite: it changes what you cook next time
and leaves every day you have already logged exactly as you ate it.

Ingredients resolve against foods only, never against recipes. A recipe built from a meal
that already contained a recipe is flattened into its parts.

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
name | food group | kJ | protein | fat | saturated | carbs | sugars | fibre |
sodium mg | alcohol g | liquid | 27 micronutrients | public food key
```

New nutrients are appended to that list rather than inserted, so the columns already
there stay lined up and the AFCD-only rows can be padded with zeros — the only honest
value, since AFCD Release 3 does not report them.

An entry logged before a nutrient existed carries no value for it, and a missing key
reads as a zero rather than as a gap. It does not have to: every entry keeps the food key
it was logged from, and an entry logged from a recipe keeps its ingredients, so the
missing keys are filled from the rebuilt database on the next load. Only absent keys are
written — amounts, portions and every nutrient already recorded are left alone. A food
typed in by hand, with no key and no ingredients, is left as it is, because there is
nothing honest to fill it from.

The public food key on the end joins each food to `MEASURES`, the portions block that
follows it. Activities and their MET values sit below both in `ACTIVITIES`.

Both blocks are generated, not hand-edited. `tools/build_ausnut.py` reads the three
FSANZ workbooks and writes them; it takes the AFCD-only rows from the commit that
introduced them rather than from the working copy, so re-running it reproduces its own
output instead of folding it back in. Point the paths at your copies of the workbooks
and run it.

The starter recipes are generated too, from `tools/recipes.json` — one entry per recipe,
ingredients as `[search query, grams for one, label]`, plus its variations and the
per-serve macros it claims. `tools/foodmap.json` pins each search query to a public food
key, because a name lookup is the wrong thing to depend on for data that ships. Optional
`image` and `source` fields ride through both scripts untouched, so a photograph or a
partner's range needs data rather than code.

    node tools/build_recipes.mjs   # resolve keys, double to two serves, check against the
                                   # claimed macros → tools/recipes.built.json
    node tools/seed_recipes.mjs    # compute per-100 g nutrition incl. micros
                                   # → tools/seed-recipes.json

The second file's contents are the `SEED_RECIPES` block in `index.html`, verbatim. Both
scripts drive the page itself through Playwright rather than reimplementing the
nutrition maths, so the seeded numbers cannot drift from what the app would compute.

## Sources

Food Standards Australia New Zealand, *AUSNUT 2023* — food nutrient profiles, food
details and food measures.
<https://www.foodstandards.gov.au/science-data/food-nutrient-databases/ausnut>

Food Standards Australia New Zealand, *Australian Food Composition Database — Release 3*.
<https://www.foodstandards.gov.au/science-data/food-nutrient-databases/afcd/data-files>

National Health and Medical Research Council, *Nutrient Reference Values for Australia
and New Zealand*. <https://www.nrv.gov.au>
