// Copy as middleware.js into the root of a static Vercel deploy.
// Logs every request (path, user agent, IP, country, referer) without changing the response.
// Read with: vercel logs <project>.vercel.app --since 30m --json  (the JSON sits in each line's "message").
export const config = { matcher: '/:path*' };
export default function middleware(request) {
  const h = request.headers;
  console.log(JSON.stringify({
    url: new URL(request.url).pathname,
    ua: h.get('user-agent'),
    ip: h.get('x-forwarded-for'),
    pais: h.get('x-vercel-ip-country'),
    ref: h.get('referer'),
    accept: (h.get('accept') || '').slice(0, 40),
    metodo: request.method,
  }));
}
