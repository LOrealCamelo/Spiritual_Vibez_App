import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../cloudflare-api.js';

const host = 'https://app.neurospicymystic.com';
const render = 'https://spiritual-vibez-app.onrender.com';
const env = {ASSETS: {fetch: async () => new Response('<html>frontend</html>', {headers: {'Content-Type': 'text/html'}})}};
const fetchOriginal = globalThis.fetch;

async function withUpstream(handler, run) {
  globalThis.fetch = handler;
  try { await run(); } finally { globalThis.fetch = fetchOriginal; }
}

test('Cloudflare serves static pages without calling Render', async () => {
  await withUpstream(() => { throw Error('Unexpected request to Render'); }, async () => {
    const response = await worker.fetch(new Request(host + '/'), env);
    assert.equal(response.status, 200);
    assert.match(await response.text(), /frontend/);
  });
});

test('health API proxies to Render and preserves response body', async () => {
  await withUpstream(async (request) => {
    assert.equal(request.url, render + '/api/health');
    assert.equal(request.method, 'GET');
    return Response.json({status: 'online', app: 'FastAPI'});
  }, async () => {
    const response = await worker.fetch(new Request(host + '/api/health'), env);
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), {status: 'online', app: 'FastAPI'});
    assert.equal(response.headers.get('cache-control'), 'no-store');
  });
});

test('location cities endpoint preserves query and original Python place IDs', async () => {
  const path = '/api/astrology/locations/cities?country=US&state=NY&query=Utica';
  await withUpstream(async (request) => {
    assert.equal(request.url, render + path);
    return Response.json({places: [{place_id: '5142056', city: 'Utica'}], total: 1});
  }, async () => {
    const response = await worker.fetch(new Request(host + path), env);
    const payload = await response.json();
    assert.equal(payload.places[0].place_id, '5142056');
    assert.equal(payload.total, 1);
  });
});

test('natal chart and all other POST APIs forward JSON bodies and status codes', async () => {
  const body = JSON.stringify({birth_date: '1996-11-05', place_id: '5142056'});
  await withUpstream(async (request) => {
    assert.equal(request.url, render + '/api/astrology/natal-chart');
    assert.equal(request.method, 'POST');
    assert.match(request.headers.get('content-type'), /application\/json/);
    assert.equal(await request.text(), body);
    return Response.json({detail: 'Please supply a birth time'}, {status: 422});
  }, async () => {
    const response = await worker.fetch(new Request(host + '/api/astrology/natal-chart', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body
    }), env);
    assert.equal(response.status, 422);
    assert.equal((await response.json()).detail, 'Please supply a birth time');
  });
});

test('all eight API router families are forwarded without route-by-route rewrites', async () => {
  const routes = ['/api/tarot/cards', '/api/synastry/life-path', '/api/rituals/search',
    '/api/wellness/health', '/api/divination/runes/cast', '/api/oracle/chat',
    '/api/store/products', '/api/astrology/moon-calendar'];
  await withUpstream(async (request) => {
    return Response.json({path: new URL(request.url).pathname});
  }, async () => {
    for (const path of routes) {
      const response = await worker.fetch(new Request(host + path), env);
      assert.equal((await response.json()).path, path);
    }
  });
});

test('Render outage returns informative 502 rather than a fake chart', async () => {
  await withUpstream(async () => { throw Error('Network timeout'); }, async () => {
    const response = await worker.fetch(new Request(host + '/api/tarot/cards'), env);
    assert.equal(response.status, 502);
    assert.equal((await response.json()).code, 'PYTHON_API_UNAVAILABLE');
    assert.equal(response.headers.get('cache-control'), 'no-store');
  });
});

test('invalid upstream configuration is rejected', async () => {
  await withUpstream(() => { throw Error('Unexpected request'); }, async () => {
    const response = await worker.fetch(new Request(host + '/api/health'), {
      ...env, PYTHON_API_ORIGIN: 'http://untrusted.example.org'
    });
    assert.equal(response.status, 500);
    assert.equal((await response.json()).code, 'API_ORIGIN_INVALID');
  });
});
