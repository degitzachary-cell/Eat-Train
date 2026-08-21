import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CHROME = process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const R = JSON.parse(fs.readFileSync(path.join(ROOT,'tools','recipes.built.json'),'utf8'));
const b = await chromium.launch({ executablePath:CHROME });
const p = await b.newPage();
await p.goto('file://' + path.join(ROOT,'index.html')); await p.waitForTimeout(1000);
const seeds = await p.evaluate(rs => rs.map(r => {
  const it = i => { const f = foodByKey(i.key);
    return {key:i.key, name:f.name, grams:i.grams, liquid:!!f.liquid, label:i.label || ''}; };
  const items = r.items.map(it);
  const t = nutritionOf(items), k = 100 / t.grams;
  const o = {name:r.name, servings:r.servings, items, method:r.method,
    tags:{cuisine:r.cuisine, base:r.base, time:r.time, meal:r.meal},
    mods:r.mods.map(m => ({name:m.name, note:m.note,
      set:m.set.map(s => ({key:s.key, grams:s.grams})),
      add:m.add.map(it)})),
    totalG:+t.grams.toFixed(1), serveG:+(t.grams / r.servings).toFixed(1),
    kj:+(t.kj*k).toFixed(2), p:+(t.p*k).toFixed(2), f:+(t.f*k).toFixed(2), sat:+(t.sat*k).toFixed(2),
    c:+(t.c*k).toFixed(2), sug:+(t.sug*k).toFixed(2), fib:+(t.fib*k).toFixed(2),
    na:+(t.na*k).toFixed(2), alc:+(t.alc*k).toFixed(2), m:{}};
  MICRO_KEYS.forEach(x => o.m[x] = +(t.m[x]*k).toFixed(4));
  return o;
}), R);
fs.writeFileSync(path.join(ROOT,'tools','seed-recipes.json'), JSON.stringify(seeds));
console.log(seeds.length, 'recipes ·', (JSON.stringify(seeds).length/1024).toFixed(1), 'KB');
console.log(seeds.map(s => s.name + ' — ' + s.items.length + ' ingredients, ' + s.mods.length + ' mods, ' +
  s.method.length + ' steps, ' + Math.round(s.serveG) + ' g/serve').join('\n'));
await b.close();
