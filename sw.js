const CACHE_NAME = 'liljr-v1';
const URLS_TO_CACHE = [
  '/phone',
  '/phone/icon.png',
  '/terminal',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(URLS_TO_CACHE)));
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});
