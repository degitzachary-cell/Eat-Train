# Coach report — content specification

A one-off PDF a coach generates on demand for one athlete. This document
specifies **what is on the page and how each number behaves**. It does not
specify how it looks — that is the designer's job, and every layout decision
below is a constraint rather than a preference.

- **Audience:** a coach deciding what to say to this athlete this week.
- **Produced by:** the coach, on demand, one athlete at a time.
- **Delivered as:** a print stylesheet plus `window.print()`. The browser makes
  the PDF; the app adds no PDF library.
- **Not in it:** the itemised food log. Decided and settled — the report is
  summary only.

---

## 1. Format constraints

These are hard limits the design has to live inside.

| Constraint | Value |
|---|---|
| Page | A4 portrait, 210 × 297 mm |
| Margins | Browser print margins apply; assume 12 mm usable edge on all sides |
| Target length | 2 pages. 3 is acceptable. 4 means something must be cut |
| Colour | Must remain readable **printed in greyscale**. Colour may carry emphasis, never meaning on its own — pair every colour cue with a symbol, weight or word |
| Interactivity | None. No hover, no tooltips, no links that matter |
| Fonts | Whatever the app already loads. No new webfonts |
| Page breaks | Every panel below must be breakable or `break-inside: avoid` as noted per panel |

**Rendering note for the designer:** the report is generated inside the
existing single-file app, so the markup is plain HTML and CSS with no build
step and no component library. Assume no CSS framework.

---

## 2. Global rules

### 2.1 The two windows

Every panel is computed twice and both are shown: **last 3 days** and
**last 7 days**, ending on the most recent complete day.

- The 3-day column answers *what is happening now*.
- The 7-day column answers *what happened this week*.
- They will frequently disagree. That is the point; do not average them away.

**Layout decision required from the designer:** side-by-side columns on every
panel, or two sequential sections. Side-by-side is denser and makes divergence
obvious; sequential is easier to read and roughly doubles the length. Pick one
and apply it to the whole document — mixing the two per panel will be
unreadable.

### 2.2 Deltas

Every delta compares a window against **the immediately preceding window of
the same length**:

- 3-day column → the 3 days before those 3
- 7-day column → the 7 days before those 7

Never compare a 3-day window against a 7-day one.

Format: signed, with the unit. `+1.2 kg`, `−340 kJ`, `+4%`. Use a true minus
sign (−), not a hyphen. Zero prints as `—`, not `0`.

### 2.3 Energy units

The report follows the athlete's own setting — kilojoules or Calories, never
both. Print the unit in the header so the coach is never guessing.

> **Open decision:** whether a coach can override this to their own preferred
> unit. Assume not, for now.

### 2.4 Rounding and widths

The designer needs to know the widest string each field can produce.

| Kind | Rounding | Widest realistic string |
|---|---|---|
| Energy, kJ | whole, thousands separator | `14,200 kJ` |
| Energy, Cal | whole, thousands separator | `3,400 Cal` |
| Macro grams | whole | `468 g` |
| Protein per kg | 1 decimal | `2.4 g/kg` |
| Weight | 1 decimal | `104.6 kg` |
| Body fat | 1 decimal | `13.8 %` |
| Micronutrient % of RDI | whole | `1,240 %` (yes, it happens — liver, supplements) |
| Micronutrient amount | 2 significant figures | `0.85 mg`, `1,100 µg` |
| Counts | whole | `7 of 7` |
| Dates | `D MMM` | `23 Aug` |

### 2.5 Direction of good

This is the trap in the whole document. **Higher is not always better, and the
design must not imply that it is.**

| Rises are good | Rises are bad | No direction |
|---|---|---|
| Protein, fibre, most micronutrients, lean mass, days logged | Sodium, saturated fat, free sugars, trans fat, alcohol, fat mass | Weight, energy intake, carbohydrate — depends entirely on the goal |

Anything in the third column must be presented neutrally. A weight rise is not
a failure; for an athlete gaining, it is the objective.

### 2.6 Empty and partial states

Every panel needs a defined appearance when there is no data. These are not
edge cases — a new athlete hits all of them at once.

- **No days logged in the window:** the panel prints its labels and `—` for
  every value, plus a single line: *"Nothing logged in this window."*
- **Some days logged:** show the figures, and the coverage count is mandatory
  and adjacent (see §3).
- **No weigh-ins in the window:** body markers show the last known reading with
  its date, and the delta prints `—` with *"no weigh-in in this window"*.
- **Never any weigh-in:** the body panel is omitted entirely rather than
  printed empty.
- **Fewer than 2 weigh-ins:** trend and rate-of-change fields print `—`; do not
  print a rate derived from one point.

---

## 3. Panel 1 — Data quality

**This panel is first, always, and cannot be moved or collapsed.** Every number
in the rest of the document is conditional on it. `break-inside: avoid`.

| Field | Format | Notes |
|---|---|---|
| Days logged | `5 of 7` | A day counts as logged if it has any food entry |
| Days with all four meals | `3 of 7` | Breakfast, lunch, dinner, snacks each non-empty |
| Days with a single entry only | `2` | Suppress the row if zero |
| Entries with no micronutrient data | `4 entries across 3 days` | Drives the caveat in Panel 6. Suppress if zero |
| Weigh-ins in window | `2` | |
| Micronutrient coverage | `4 of 7 days complete` | Days where every logged entry carried a micro profile |

**Fixed caveat text, printed on the page, not in a footnote:**

> Self-reported intake is under-reported by 20–30% in the published
> literature, consistently and across populations. Read the totals below as a
> floor, not a measurement.

**Design note:** this panel must not look like an error state or a warning. It
is context, and it is normal for it to be imperfect. If it reads as a telling-
off, coaches will learn to skip it.

---

## 4. Panel 2 — Body markers

One row per marker. Omit any row the athlete has never recorded — do not print
empty rows for markers this person does not measure.

Each row carries four values:

1. **Current** — the most recent reading
2. **Change vs previous reading** — signed
3. **Date of that previous reading** — `D MMM`
4. **Change across the window** — signed

| Marker | Unit | Precision | Notes |
|---|---|---|---|
| Weight, last reading | kg | 1 dp | The raw number off the scale |
| **Weight, trend** | kg | 1 dp | **Separate row.** The app runs on the trend, not the last reading. They differ, often by more than a kilo, and the coach needs both |
| Body fat | % | 1 dp | |
| Fat mass | kg | 1 dp | Derived: weight × body fat %. This is the row that moves meaningfully |
| Skeletal muscle mass | kg | 1 dp | |
| Lean mass | kg | 1 dp | Derived: weight − fat mass |
| Bone mineral | kg | 1 dp | Omit unless recorded |
| Body water | % | 1 dp | Omit unless recorded |
| Measured maintenance | energy | whole | Only if the app's 28-day estimate is live; otherwise omit the row |

**Rate of change block** — two numbers side by side, and the most useful thing
on the page:

| Field | Format |
|---|---|
| Actual rate | `−0.35 kg/week` |
| Predicted from logged intake | `−0.62 kg/week` |

Predicted comes from the logged energy balance. When these two disagree, either
the logging is incomplete or the target is wrong, and that is the conversation
the coach needs to have. **Print them adjacent and make the comparison
unavoidable.** Do not editorialise which is right.

Requires at least 2 weigh-ins spanning the window; otherwise both print `—`.

---

## 5. Panel 3 — Energy

### 5.1 Per-day table

One row per day in the window. Seven rows maximum.

| Column | Format |
|---|---|
| Date | `Mon 18 Aug` |
| Eaten | energy, whole |
| Target | energy, whole |
| Balance | signed energy |
| Training that day | `Y`/blank, or session count |

Days with nothing logged still get a row, marked *not logged* — a gap in the
week is information, and dropping the row hides it.

### 5.2 Window figures

| Field | Format | Notes |
|---|---|---|
| Average eaten | energy/day | Over logged days only. State the divisor: `2,140 Cal over 5 logged days` |
| Average target | energy/day | |
| Average balance | signed energy/day | |
| Target basis | word | `formula`, `coached`, or `measured` — the coach needs to know where the target came from |
| **Day-to-day variability** | signed energy | Standard deviation of daily intake. 2,000 every day and 1,200/3,000 alternating average identically and are entirely different problems |
| Training-day average | energy/day | |
| Rest-day average | energy/day | |
| Largest surplus day | `+1,240 · Sat 23 Aug` | |
| Largest deficit day | `−980 · Tue 19 Aug` | |

---

## 6. Panel 4 — The meal grid

The centrepiece. One block per day; within each day, one row per meal.

**Columns:** Energy · Protein · Carbs · Fat · Fibre

**Rows:** Breakfast · Lunch · Dinner · **Snacks** · Day total

Snacks is its own row and is never folded into the others. It is frequently
where the gap between what someone believes they ate and what they logged
sits, and hiding it defeats the panel.

Under the whole grid, a **window average row per meal** — average breakfast,
average lunch, average dinner, average snacks across the window.

Optional, designer's call on whether it fits: **first and last entry time per
day**, which shows the eating window without needing a separate panel.

**Layout constraints:**
- 7 days × 5 rows = 35 rows plus headers. This panel will dominate the
  document and probably owns a page of its own.
- It must break across pages cleanly, repeating the column header.
- Empty meals print `—` across, not zeros. A skipped breakfast and a breakfast
  of zero calories are different claims.

---

## 7. Panel 5 — Macros

| Field | Format | Notes |
|---|---|---|
| Protein | `g` and `% of energy` and `vs target` | |
| **Protein per kg bodyweight** | `1.8 g/kg` | Its own line, prominent. The number coaches actually use |
| Carbohydrate | `g`, `% of energy`, `vs target` | |
| Fat | `g`, `% of energy`, `vs target` | |
| Fibre | `g vs 30 g` (male) / `25 g` (female) | |
| Saturated fat | `g`, `% of energy` | A limit, not a target |
| Free sugars | `g vs limit` | Limit is 10% of energy |
| Trans fat | `mg vs limit` | Limit is 1% of energy |
| Alcohol | `g` and `% of week's energy` | Suppress the row entirely if zero across the window |
| Sodium | `mg vs upper level` | **Presented as a ceiling.** High is the problem. Must not use the same visual treatment as a nutrient the athlete is trying to reach |

---

## 8. Panel 6 — Micronutrients

Against NHMRC / New Zealand Nutrient Reference Values, read for the athlete's
sex and age. **Four buckets, never one list.**

| Bucket | Threshold | Ordering |
|---|---|---|
| **Hit** | ≥100% of RDI, window average | Alphabetical. These need no attention; keep them compact |
| **Borderline** | 70–99% | Descending severity |
| **Short** | <70% | **Ascending — worst first.** This is the actionable list |
| **Over the upper limit** | >UL | Separate and flagged. More is not better |

Each entry in **Short** carries:

- Nutrient name
- Average intake with unit
- % of RDI
- **Largest contributing food** — e.g. *"iron 46% — most of it from Tuesday's steak"*. Without this the coach knows there is a problem but not what to say about it.

**Special cases the design must accommodate:**

- **Sodium** is a ceiling, not a goal. It inverts. It appears in Panel 5, not here — do not duplicate it into the shortfall list where low would read as bad.
- **Free sugars** and **trans fat** are limits. Same reasoning; they live in Panel 5.
- **Caffeine** has no RDI, only a caution threshold. It cannot appear in any of the four buckets. Give it its own line if it is non-zero.
- **Vitamin A** reads against retinol equivalents, **folate** against dietary folate equivalents. The label should say so, because the number will not match the back of a supplement bottle.
- Some nutrients have an **adequate intake** or a **suggested dietary target** rather than an RDI. Label which reference each is read against; they are not interchangeable.

**Mandatory adjacent line:**

> Micronutrient data complete on 4 of 7 days.

Without it, a shortfall list is measuring the food database, not the person —
a food logged with no micronutrient profile reads as zero and drags every
average down. This line is not optional and must not be relegated to a
footnote.

---

## 9. Panel 7 — Training and hydration

| Field | Format |
|---|---|
| Sessions | count, by type |
| Session minutes | total |
| Session energy | total |
| Steps | daily average |
| Energy from steps | total |
| Load vs previous window | signed % or signed energy |
| Water | daily average vs target |

Water target is the NHMRC fluid adequate intake plus the day's training
allowance. If the athlete does not log water, omit the row rather than
printing zero — an unlogged drink is not an undrunk one.

---

## 10. Explicitly out of scope

- The itemised food log. Settled.
- Anything the coach can edit. This document is read-only by construction.
- Photographs, barcodes, product names beyond the "largest contributor" line.
- Comparison against other athletes.

---

## 11. Open decisions for the designer

1. **Side-by-side or sequential** for the 3-day and 7-day windows. Applies to
   the whole document, not per panel.
2. **Meal timing** in Panel 4 — include first/last entry per day, or drop it.
3. **Page-one priority.** If only one page were read, it should carry data
   quality, body markers and the rate-of-change comparison. Everything else can
   fall to page two.
