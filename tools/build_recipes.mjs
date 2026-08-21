import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CHROME = process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const R = JSON.parse(fs.readFileSync(path.join(ROOT,'tools','recipes.json'),'utf8'));
const MAP = JSON.parse(fs.readFileSync(path.join(ROOT,'tools','foodmap.json'),'utf8'));
const SERVES = 2;   // written for one; doubled so a batch feeds two and one serve is the original

const recipes = R.map(r => {
  const items = r.items.map(([q, g, label]) => ({key:MAP[q], q, grams:+(g*SERVES).toFixed(1), label}));
  const mods = (r.mods||[]).map(m => ({
    name:m.name, note:m.note,
    set:(m.set||[]).map(([q,g]) => ({key:MAP[q], grams:+(g*SERVES).toFixed(1)})),
    add:(m.add||[]).map(([q,g,label]) => ({key:MAP[q], grams:+(g*SERVES).toFixed(1), label}))
  }));
  return {name:r.name, servings:SERVES, cuisine:r.cuisine, base:r.base, time:r.time,
          meal:r.meal, items, method:r.method, mods, check:r.check,
          // Carried through so a photograph or a partner kitchen's dish needs
          // no change to the pipeline, only a field in recipes.json.
          image:r.image || '', source:r.source || ''};
});

const b = await chromium.launch({ executablePath:CHROME });
const p = await b.newPage();
await p.goto('file://' + path.join(ROOT,'index.html')); await p.waitForTimeout(1000);
const report = await p.evaluate(rs => {
  const KCAL = 4.184;
  return rs.map(r => {
    const items = r.items.map(i => ({key:i.key, name:(foodByKey(i.key)||{}).name || ('MISSING '+i.key),
                                     grams:i.grams, liquid:!!(foodByKey(i.key)||{}).liquid, label:i.label}));
    const t = nutritionOf(items);
    const per = n => n / r.servings;
    return { name:r.name, missing: items.filter(i => i.name.startsWith('MISSING')).map(i=>i.key),
      got:{kcal:Math.round(per(t.kj)/KCAL), p:Math.round(per(t.p)), c:Math.round(per(t.c)), f:Math.round(per(t.f))},
      want:r.check,
      fibre:+per(t.fib).toFixed(1), na:Math.round(per(t.na)),
      resolved: items.map(i => i.name) };
  });
}, recipes);

console.log('recipe'.padEnd(38), 'computed / stated per serve');
let bad = 0;
for (const r of report) {
  const d = k => r.got[k] - r.want[k];
  const pct = Math.abs(d('kcal')) / r.want.kcal * 100;
  const flag = pct > 15 ? ' ✗' : (pct > 8 ? ' ~' : ' ✓');
  if (pct > 15) bad++;
  console.log(r.name.padEnd(38),
    `${r.got.kcal}/${r.want.kcal} kcal  P ${r.got.p}/${r.want.p}  C ${r.got.c}/${r.want.c}  F ${r.got.f}/${r.want.f}` +
    `   fibre ${r.fibre} g  Na ${r.na} mg${flag}`);
  if (r.missing.length) console.log('    MISSING KEYS:', r.missing.join(', '));
}
console.log('\n' + bad + ' recipes more than 15% off the stated energy');
fs.writeFileSync(path.join(ROOT,'tools','recipes.built.json'), JSON.stringify(recipes,null,1));
await b.close();
