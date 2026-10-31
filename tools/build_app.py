"""Builds the installable app in app/ from the single-page source index.html.

The source page is written for the Claude artifact viewer (no <head>, Google-hosted fonts).
This script wraps it in a full HTML document, swaps in the bundled fonts, and adds the
web-app manifest, iOS home-screen tags and an offline service worker.

Run from the project root:  python3 tools/build_app.py
"""
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
OUT = ROOT / "app"

NAME = "Training Program"
SHORT = "Training"
DESC = "Push/pull/legs and glute-focused workout programs with animated exercise demos and a set and rest timer."

src = SRC.read_text(encoding="utf-8")

# Pull the <title> out (it moves into <head>) and drop the Google Fonts tags.
title = re.search(r"<title>(.*?)</title>", src).group(1)
body = re.sub(r"<title>.*?</title>\n?", "", src, count=1)
body = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', "", body)
body = re.sub(r'<link rel="preconnect"[^>]*>\n?', "", body)
body = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n?', "", body)

head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{DESC}">
<meta name="theme-color" content="#eef0ec" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141917" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" href="icons/favicon.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="{SHORT}">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="stylesheet" href="fonts/fonts.css">
<style>
:root {{ color-scheme: light; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }}
body {{ margin: 0; font: 14px system-ui, -apple-system, sans-serif; overscroll-behavior-y: none; }}
img {{ max-width: 100%; }}
[hidden] {{ display: none !important; }}
button {{ touch-action: manipulation; -webkit-user-select: none; user-select: none; }}
</style>
</head>
<body>
"""

sw_register = """
<script>
// Offline support. Skipped inside the native (Capacitor) shell, where files are already local.
if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost") && !window.Capacitor) {
  addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
}
</script>
</body>
</html>
"""

OUT.mkdir(exist_ok=True)
(OUT / "index.html").write_text(head + body + sw_register, encoding="utf-8")

manifest = {
    "name": NAME,
    "short_name": SHORT,
    "description": DESC,
    "id": "./",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#eef0ec",
    "theme_color": "#d9480f",
    "categories": ["health", "fitness", "sports"],
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
(OUT / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

# Every file the app needs offline. The cache name changes whenever any of them changes,
# so installed copies pick up new versions on their next launch.
files = ["./", "index.html", "manifest.webmanifest"] + sorted(
    str(p.relative_to(OUT)) for p in OUT.rglob("*")
    if p.is_file() and p.suffix in {".png", ".ttf", ".css"}
)
digest = hashlib.sha256()
for f in files[1:]:
    digest.update((OUT / f).read_bytes())
version = digest.hexdigest()[:10]

sw = f"""// Service worker: caches the whole app so it opens and runs with no connection.
const CACHE = "training-program-{version}";
const FILES = {json.dumps(files, indent=2)};

self.addEventListener("install", e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
}});
self.addEventListener("activate", e => {{
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
}});
self.addEventListener("fetch", e => {{
  if (e.request.method !== "GET") return;
  e.respondWith(caches.match(e.request, {{ ignoreSearch: true }}).then(hit => hit || fetch(e.request)));
}});
"""
(OUT / "sw.js").write_text(sw, encoding="utf-8")
print(f"Built {OUT} (cache version {version}, {len(files)} files)")
