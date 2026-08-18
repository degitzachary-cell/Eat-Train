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

AFCD covers generic foods, not every supermarket line. For a branded product, copy its
Nutrition Information Panel into **New food**, or load a CSV of them at once — columns
are matched by name.

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
