// Service Worker DarmaSala Portal Alumnos
// Estrategia: network-first para HTML/JSON, cache-first para estáticos.

const CACHE_VERSION = 'darmasala-portal-v1';
const STATIC_CACHE  = `${CACHE_VERSION}-static`;
const RUNTIME_CACHE = `${CACHE_VERSION}-runtime`;

const PRECACHE_URLS = [
  '/portal/dashboard',
  '/static/img/logo_darmasala.png',
  '/static/img/yoga_bg.png',
  '/static/favicon.ico',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => cache.addAll(PRECACHE_URLS).catch(() => {}))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) => Promise.all(
      names
        .filter((n) => !n.startsWith(CACHE_VERSION))
        .map((n) => caches.delete(n))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Network-first para navegaciones y JSON
  const isNav   = req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html');
  const isJson  = url.pathname.startsWith('/portal/eventos') || url.pathname.endsWith('.json');

  if (isNav || isJson) {
    event.respondWith(networkFirst(req));
    return;
  }

  // Cache-first para estáticos
  if (url.pathname.startsWith('/static/') || url.pathname.startsWith('/portal/icons/')) {
    event.respondWith(cacheFirst(req));
    return;
  }
});

async function networkFirst(req) {
  try {
    const fresh = await fetch(req);
    if (fresh && fresh.status === 200) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(req, fresh.clone());
    }
    return fresh;
  } catch (err) {
    const cached = await caches.match(req);
    if (cached) return cached;
    // Fallback básico para navegaciones offline
    if (req.mode === 'navigate') {
      const shell = await caches.match('/portal/dashboard');
      if (shell) return shell;
    }
    throw err;
  }
}

async function cacheFirst(req) {
  const cached = await caches.match(req);
  if (cached) return cached;
  const fresh = await fetch(req);
  if (fresh && fresh.status === 200) {
    const cache = await caches.open(STATIC_CACHE);
    cache.put(req, fresh.clone());
  }
  return fresh;
}
