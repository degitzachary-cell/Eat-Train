# Eat & Train

A calorie and training tracker in a single HTML file, built on the **Australian Food
Composition Database, Release 3** (FSANZ). No build step, no server, no account —
open `index.html` and it works, including with no signal.

## What it does

- **Today** — an energy budget you can read at a glance: what you burn, what you have
  eaten, what is left. Meals, macros, fibre, saturated fat, sodium and alcohol.
- **Food** — the full AFCD, 1,588 foods, searchable, with your own products alongside.
- **Train** — MET-based session energy from the Compendium of Physical Activities,
  plus a strength log for sets, reps and volume.
- **Body** — your markers, three resting-rate models, and your goal.
- **Trends** — 14-day energy, weight trend, body composition, and your *measured*
  expenditure worked out from your own data.

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
