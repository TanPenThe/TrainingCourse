// Service worker: caches the whole app so it opens and runs with no connection.
const CACHE = "training-program-049fe0f3a6";
const FILES = [
  "./",
  "index.html",
  "manifest.webmanifest",
  "fonts/Barlow-400.ttf",
  "fonts/Barlow-500.ttf",
  "fonts/Barlow-600.ttf",
  "fonts/Barlow-700.ttf",
  "fonts/BigShouldersDisplay-700.ttf",
  "fonts/BigShouldersDisplay-900.ttf",
  "fonts/fonts.css",
  "icons/apple-touch-icon.png",
  "icons/favicon.png",
  "icons/icon-1024.png",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/maskable-512.png"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(hit => hit || fetch(e.request)));
});
