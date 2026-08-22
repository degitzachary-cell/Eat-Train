/* Open Food Facts, asked from a server instead of from the phone.

   Three things a browser cannot do, and all three are why the direct routes
   come back as "Load failed" rather than as an HTTP status:

   1. Open Food Facts asks every caller to identify itself with a User-Agent.
      `User-Agent` is a forbidden header in fetch — the browser drops it — so
      a page can only ever knock anonymously, and their edge is entitled to
      turn that away.
   2. A block or a rate-limit served without an Access-Control-Allow-Origin
      header is invisible to the page: the browser refuses to hand over the
      response, and fetch rejects with a network error carrying no status.
      From the inside, being banned and being offline look identical.
   3. POST /search with a JSON body needs a CORS preflight, which is a second
      request that can be refused on its own.

   Here there is no origin, no preflight, and a name on the request.

   No JWT: food lookup has to work before you sign in, and nothing about the
   caller is forwarded — one search term goes out, product data comes back. */

const UA = 'TrueCount/1.0 (https://degitzachary-cell.github.io/Eat-Train/)';
const FIELDS = 'code,product_name,generic_name,brands,quantity,nutriments';
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, apikey, content-type, x-client-info',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
};

function reply(body: unknown, status = 200, route = '') {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS, 'Content-Type': 'application/json', 'x-off-route': route }
  });
}

async function ask(url: string) {
  const res = await fetch(url, {
    headers: { 'User-Agent': UA, 'Accept': 'application/json' },
    signal: AbortSignal.timeout(8000)
  });
  if (!res.ok) throw new Error('http ' + res.status);
  return await res.json();
}

/* Their own shapes, kept: hits from search-a-licious, products from the
   legacy CGI, product from a read. The app already knows all three. */
function rowsOf(j: any): any[] {
  if (!j) return [];
  if (Array.isArray(j.hits)) return j.hits;
  if (Array.isArray(j.products)) return j.products;
  if (j.product) return [j.product];
  return [];
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS });

  let q = '', code = '';
  try {
    const u = new URL(req.url);
    q = (u.searchParams.get('q') || '').trim();
    code = (u.searchParams.get('code') || '').replace(/\D/g, '');
    if (req.method === 'POST') {
      const b = await req.json().catch(() => ({}));
      q = String(b.q || q).trim();
      code = String(b.code || code).replace(/\D/g, '');
    }
  } catch (_e) { /* fall through to the empty check */ }

  if (!q && !code) return reply({ error: 'pass q or code' }, 400);
  if (q.length > 80) q = q.slice(0, 80);

  const routes = code
    ? [{ n: 'v2 product', u: `https://world.openfoodfacts.org/api/v2/product/${code}.json?fields=${FIELDS}` },
       { n: 'v3 product', u: `https://world.openfoodfacts.org/api/v3/product/${code}` }]
    : [{ n: 'search-a-licious', u: `https://search.openfoodfacts.org/search?q=${encodeURIComponent(q)}&page_size=20` },
       { n: 'legacy cgi', u: `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(q)}` +
           `&search_simple=1&action=process&json=1&page_size=20&fields=${FIELDS}` }];

  const tried: string[] = [];
  for (const r of routes) {
    try {
      const j = await ask(r.u);
      const hits = rowsOf(j);
      if (!hits.length) { tried.push(r.n + ' empty'); continue; }
      return reply({ hits, via: r.n }, 200, r.n);
    } catch (e) {
      tried.push(r.n + ' ' + (e instanceof Error ? e.message : 'failed'));
    }
  }
  /* 200 with an empty hits array: nothing found and nothing broken are both
     ordinary answers, and the app tells them apart by `tried`. */
  return reply({ hits: [], tried }, 200, 'none');
});
