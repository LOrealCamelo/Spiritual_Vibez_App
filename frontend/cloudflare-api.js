/* Same-origin API bridge from Cloudflare Workers to the existing FastAPI service.
 * Every /api route is handled by Python on Render; static files stay on Cloudflare.
 * In particular, location lookup IDs and chart calculation share one dataset.
 */
const DEFAULT_API_ORIGIN = 'https://spiritual-vibez-app.onrender.com';
const json = (data, status) => new Response(JSON.stringify(data), {
  status,
  headers: {'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store'}
});

export default {
  async fetch(request, env) {
    const incoming = new URL(request.url);
    const api = incoming.pathname === '/api' || incoming.pathname.startsWith('/api/');
    const tarotAsset = incoming.pathname.startsWith('/assets/tarot/');
    if (!api && !tarotAsset) return env.ASSETS.fetch(request);
    // The 78 tarot PNGs are mounted by FastAPI, not stored in frontend/assets.
    if (tarotAsset && !['GET', 'HEAD'].includes(request.method)) {
      return json({detail: 'Method not allowed'}, 405);
    }

    // Only trusted deployment configuration can choose the upstream host.
    let origin;
    try {
      origin = new URL(env.PYTHON_API_ORIGIN || DEFAULT_API_ORIGIN);
      if (origin.protocol !== 'https:' || origin.pathname !== '/' || origin.search ||
          origin.hash || origin.username || origin.password) throw new Error('Invalid API origin');
    } catch {
      return json({detail: 'The API origin is misconfigured.', code: 'API_ORIGIN_INVALID'}, 500);
    }

    const target = new URL(incoming.pathname + incoming.search, origin);
    try {
      // Preserve original method, query, body, and content type. Do not redirect
      // API calls to the Render domain, since they are same-origin for the app.
      const upstream = await fetch(new Request(target.toString(), request), {redirect: 'manual'});
      const headers = new Headers(upstream.headers);
      if (api) headers.set('Cache-Control', 'no-store');
      return new Response(upstream.body, {
        status: upstream.status,
        statusText: upstream.statusText,
        headers
      });
    } catch {
      return json({
        detail: 'The Python API is temporarily unavailable. Please try again.',
        code: 'PYTHON_API_UNAVAILABLE'
      }, 502);
    }
  }
};
