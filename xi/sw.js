const CACHE = 'xi-v2';
const BASE = new URL('.', self.location).pathname; // 兼容根目录与子目录部署

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c =>
    c.addAll([BASE, BASE + 'index.html', BASE + 'manifest.json']).catch(()=>{})
  ));
  self.skipWaiting();
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch', e => {
  // 仅离线兜底：缓存优先，失败回退到首页
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request).catch(() => caches.match(BASE + 'index.html')))
  );
});
