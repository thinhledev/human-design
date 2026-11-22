#!/usr/bin/env python3
"""Render a page in headless Chrome, save screenshots, and measure what was drawn.

Usage:
  python3 render_check.py mockup.html --out shots/
  python3 render_check.py http://localhost:3000/pricing --widths 390,820,1440 --schemes light,dark
  python3 render_check.py page.html --squint --fold --json
  python3 render_check.py page.html --chrome "/path/to/chrome"

A design is not finished until someone has looked at it. This script gives the
agent eyes and a ruler: for each width and colour scheme it saves a screenshot
(open them and look), and it reports measured facts from the rendered page:

  type      families really used and whether each one loaded or silently fell back,
            distinct sizes and weights, characters per line of running text
  colour    text and background pairs under WCAG contrast, text over images or
            gradients (check by eye), share of gradient fills
  layout    horizontal overflow, clipped text, share of centred text, spacing
            values off the 4px grid, distinct radii and shadows
  touch     interactive targets under 24px (WCAG 2.2) and under 44px on phones
  content   images without size or alt, broken images, heading order
  motion    animations that keep running under prefers-reduced-motion
  the fold  what the first screen shows: largest text, number of controls

--squint adds a blurred greyscale screenshot: if the hierarchy is not obvious
there, it is not obvious. --fold captures only the first screen.

It talks only to the Chrome it starts, on 127.0.0.1, through the DevTools
protocol; it sends nothing anywhere else. Needs Chrome, Chromium or Edge.
Standard library only.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

MEASURE = r"""
(async () => {
  try { await Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 3000))]); } catch (e) {}
  const W = window.__hdW || innerWidth, H = innerHeight, out = {viewport: [W, H]};
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', {willReadFrequently: true}); const cache = new Map();
  const rgba = c => { if (cache.has(c)) return cache.get(c); cx.clearRect(0,0,1,1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0,0,1,1);
    const d = cx.getImageData(0,0,1,1).data; const v = [d[0]/255, d[1]/255, d[2]/255, d[3]/255]; cache.set(c, v); return v; };
  const lin = c => c <= 0.04045 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4);
  const lum = c => 0.2126*lin(c[0]) + 0.7152*lin(c[1]) + 0.0722*lin(c[2]);
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05); };
  const over = (f, b) => [0,1,2].map(i => f[i]*f[3] + b[i]*(1-f[3])).concat([1]);
  const hex = c => '#' + [0,1,2].map(i => Math.round(c[i]*255).toString(16).padStart(2,'0')).join('');
  const label = el => { let s = el.tagName.toLowerCase(); if (el.id) s += '#' + el.id;
    const c = (el.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean).slice(0,2).join('.'); if (c) s += '.' + c; return s; };
  const visible = el => { const r = el.getBoundingClientRect(); if (r.width < 1 || r.height < 1) return false;
    const s = getComputedStyle(el); return s.visibility !== 'hidden' && s.display !== 'none' && parseFloat(s.opacity) > 0.05; };
  const bgOf = el => { let node = el, layers = [], image = false;
    while (node && node.nodeType === 1) { const s = getComputedStyle(node);
      if (s.backgroundImage && s.backgroundImage !== 'none') image = true;
      const c = rgba(s.backgroundColor); if (c[3] > 0) { layers.push(c); if (c[3] >= 0.99) break; }
      node = node.parentElement; }
    let base = [1,1,1,1]; const root = rgba(getComputedStyle(document.documentElement).backgroundColor);
    if (!layers.length || layers[layers.length-1][3] < 0.99) base = root[3] > 0 ? over(root, [1,1,1,1]) : (matchMedia('(prefers-color-scheme: dark)').matches && getComputedStyle(document.documentElement).colorScheme.includes('dark') ? [0.07,0.07,0.07,1] : [1,1,1,1]);
    for (let i = layers.length - 1; i >= 0; i--) base = over(layers[i], base);
    return {color: base, image}; };
  // font fallback detection by width comparison
  const fontOk = name => { const t = 'mmmmmmmmmmlliWW@#0O1Il', m = document.createElement('canvas').getContext('2d');
    const w = f => { m.font = '72px ' + f; return m.measureText(t).width; };
    const q = '"' + name.replace(/"/g, '') + '"';
    return ['monospace', 'serif', 'sans-serif'].some(g => Math.abs(w(q + ',' + g) - w(g)) > 0.5); };
  const generic = new Set(['serif','sans-serif','monospace','system-ui','ui-sans-serif','ui-serif','ui-monospace','ui-rounded','cursive','fantasy','-apple-system','blinkmacsystemfont','emoji','math']);
  const fam = {}, sizes = {}, weights = {}, colors = {}, low = [], overImage = [], measures = [], clipped = [];
  let chars = 0, centered = 0, gradientText = 0;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  while (walker.nextNode()) {
    const tn = walker.currentNode, txt = tn.nodeValue.replace(/\s+/g, ' ').trim(); if (txt.length < 2) continue;
    const el = tn.parentElement; if (!el || seen.has(el) || !visible(el)) continue;
    if (['SCRIPT','STYLE','NOSCRIPT','TEMPLATE','OPTION'].includes(el.tagName)) continue;
    seen.add(el);
    const s = getComputedStyle(el), n = (el.innerText || txt).replace(/\s+/g, ' ').trim().length; if (!n) continue;
    chars += n;
    const first = s.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, '');
    fam[first] = (fam[first] || 0) + n;
    const px = Math.round(parseFloat(s.fontSize) * 10) / 10; sizes[px] = (sizes[px] || 0) + n;
    weights[s.fontWeight] = (weights[s.fontWeight] || 0) + n;
    if (s.textAlign === 'center' || s.textAlign === '-webkit-center') centered += n;
    if (el.closest(':disabled, [aria-disabled="true"], [inert]')) continue;
    const clip = s.webkitBackgroundClip === 'text' || s.backgroundClip === 'text';
    if (clip) { gradientText += 1; continue; }
    const fg = rgba(s.color), bg = bgOf(el), eff = over(fg, bg.color), r = ratio(eff, bg.color);
    colors[hex(eff)] = (colors[hex(eff)] || 0) + n;
    const big = px >= 24 || (px >= 18.66 && parseInt(s.fontWeight) >= 700), need = big ? 3 : 4.5;
    if (bg.image) { if (overImage.length < 8) overImage.push({el: label(el), text: txt.slice(0, 40), size: px}); }
    else if (r < need - 0.01) low.push({el: label(el), text: txt.slice(0, 40), ratio: Math.round(r*100)/100, need, size: px, fg: hex(eff), bg: hex(bg.color), chars: n});
    if (n >= 140 && s.display !== 'inline') { const range = document.createRange(); range.selectNodeContents(el);
      const tops = new Set([...range.getClientRects()].map(q => Math.round(q.top))); const lines = Math.max(1, tops.size);
      if (lines >= 3) measures.push({el: label(el), cpl: Math.round(n / lines), size: px, line: Math.round(parseFloat(s.lineHeight) / px * 100) / 100 || null}); }
    if ((s.overflow === 'hidden' || s.overflowY === 'hidden') && el.scrollHeight > el.clientHeight + 3 && s.webkitLineClamp === 'none' && clipped.length < 6) clipped.push({el: label(el), text: txt.slice(0, 40)});
  }
  out.chars = chars;
  out.families = Object.entries(fam).sort((a,b) => b[1]-a[1]).slice(0, 8).map(([name, n]) => ({name, share: n/chars, generic: generic.has(name.toLowerCase()), loaded: generic.has(name.toLowerCase()) ? true : fontOk(name)}));
  out.sizes = Object.entries(sizes).map(([k, n]) => [parseFloat(k), n/chars]).sort((a,b) => a[0]-b[0]);
  out.weights = Object.entries(weights).map(([k, n]) => [k, n/chars]).sort((a,b) => b[1]-a[1]);
  out.textColors = Object.entries(colors).sort((a,b) => b[1]-a[1]).slice(0, 12).map(([k, n]) => [k, n/chars]);
  out.textColorCount = Object.keys(colors).length;
  out.centeredShare = chars ? centered / chars : 0;
  out.gradientText = gradientText;
  out.lowContrast = low.sort((a,b) => b.chars - a.chars).slice(0, 12); out.lowContrastCount = low.length;
  out.overImage = overImage; out.measures = measures.slice(0, 12); out.clipped = clipped;
  // boxes: spacing, radius, shadow, gradients, backgrounds
  const spacing = {}, radii = {}, shadows = new Set(), bgs = {}; let gradients = 0, boxes = 0, blur = 0;
  for (const el of document.body.querySelectorAll('*')) { if (!visible(el)) continue; const s = getComputedStyle(el); boxes++;
    for (const p of ['paddingTop','paddingRight','paddingBottom','paddingLeft','rowGap','columnGap','marginTop','marginBottom']) {
      const v = parseFloat(s[p]); if (v > 0 && v < 400) { const k = Math.round(v * 2) / 2; spacing[k] = (spacing[k] || 0) + 1; } }
    const r = s.borderTopLeftRadius; const rect = el.getBoundingClientRect();
    if (r && r !== '0px' && rect.width > 24) { const pill = parseFloat(r) >= Math.min(rect.width, rect.height) / 2 - 1; const k = pill ? 'pill' : r; radii[k] = (radii[k] || 0) + 1; }
    if (s.boxShadow && s.boxShadow !== 'none') shadows.add(s.boxShadow);
    if (/gradient\(/.test(s.backgroundImage) && rect.width > 40 && rect.height > 20) gradients++;
    if (s.backdropFilter && s.backdropFilter !== 'none') blur++;
    const c = rgba(s.backgroundColor); if (c[3] > 0.5 && rect.width * rect.height > 4000) { const k = hex(c); bgs[k] = (bgs[k] || 0) + rect.width * rect.height; } }
  const sp = Object.entries(spacing).map(([k, n]) => [parseFloat(k), n]); const spTotal = sp.reduce((a, b) => a + b[1], 0) || 1;
  out.spacing = {distinct: sp.length, offGrid: sp.filter(([k]) => k % 4 !== 0 && k > 2).sort((a,b) => b[1]-a[1]).slice(0, 8), offGridShare: sp.filter(([k]) => k % 4 !== 0 && k > 2).reduce((a, b) => a + b[1], 0) / spTotal};
  out.radii = Object.entries(radii).sort((a,b) => b[1]-a[1]).slice(0, 8); out.shadows = shadows.size; out.gradients = gradients; out.backdropBlur = blur; out.boxes = boxes;
  out.backgrounds = Object.entries(bgs).sort((a,b) => b[1]-a[1]).slice(0, 6).map(([k]) => k);
  // overflow
  const sw = document.documentElement.scrollWidth; out.overflowX = sw > W + 1 ? sw - W : 0; out.overflowers = [];
  if (out.overflowX) for (const el of document.body.querySelectorAll('*')) { const r = el.getBoundingClientRect(); if (r.right > W + 1 && r.width > 0 && out.overflowers.length < 6 && visible(el)) { const s = getComputedStyle(el); if (s.position !== 'fixed') out.overflowers.push(label(el) + ' right=' + Math.round(r.right)); } }
  out.pageHeight = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);
  // targets
  const small = [], cramped = []; let controls = 0, foldControls = 0;
  for (const el of document.querySelectorAll('a[href], button, input:not([type=hidden]), select, textarea, [role=button], [role=link], [role=tab], [role=menuitem], [role=checkbox], [role=switch], summary')) {
    if (!visible(el)) continue; controls++; const r = el.getBoundingClientRect(); if (r.top < H && r.bottom > 0) foldControls++;
    const s = getComputedStyle(el); const inline = s.display === 'inline' && el.tagName === 'A' && el.parentElement && el.parentElement.innerText.trim().length > (el.innerText || '').trim().length + 10;
    if (inline) continue;
    if (r.width < 24 || r.height < 24) { if (small.length < 10) small.push(label(el) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height)); }
    else if (W <= 600 && (r.width < 44 || r.height < 44)) { if (cramped.length < 10) cramped.push(label(el) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height)); } }
  out.controls = controls; out.smallTargets = small; out.crampedTargets = cramped;
  // images and headings
  out.images = {total: 0, noAlt: 0, noSize: 0, broken: 0};
  for (const im of document.images) { if (!visible(im)) continue; out.images.total++; if (!im.hasAttribute('alt')) out.images.noAlt++;
    if (!(im.getAttribute('width') && im.getAttribute('height')) && getComputedStyle(im).aspectRatio === 'auto') out.images.noSize++; if (im.complete && im.naturalWidth === 0) out.images.broken++; }
  const hs = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(visible).map(h => parseInt(h.tagName[1]));
  out.headings = {h1: hs.filter(x => x === 1).length, total: hs.length, skips: hs.filter((x, i) => i > 0 && x > hs[i-1] + 1).length};
  // the first screen
  let big = null; for (const el of seen) { const r = el.getBoundingClientRect(); if (r.top >= H || r.bottom <= 0) continue; const px = parseFloat(getComputedStyle(el).fontSize);
    if (!big || px > big.size) big = {size: px, text: (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 80), el: label(el)}; }
  out.fold = {largest: big, controls: foldControls};
  out.animations = document.getAnimations ? document.getAnimations().filter(a => a.playState === 'running').length : 0;
  out.infinite = document.getAnimations ? document.getAnimations().filter(a => a.effect && a.effect.getTiming && a.effect.getTiming().iterations === Infinity).length : 0;
  out.title = document.title; out.lang = document.documentElement.lang || '';
  return JSON.stringify(out);
})()
"""


def find_chrome(given=None):
    if given:
        return given
    for c in CANDIDATES:
        if os.path.isabs(c) and os.path.exists(c):
            return c
        found = shutil.which(c)
        if found:
            return found
    return None


class CDP:
    """A minimal DevTools-protocol client over one WebSocket (text frames only)."""

    def __init__(self, ws_url: str, timeout: float = 30.0):
        u = urllib.parse.urlsplit(ws_url)
        self.sock = socket.create_connection((u.hostname, u.port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("Chrome closed the connection during the handshake")
            buf += chunk
        if b" 101 " not in buf.split(b"\r\n", 1)[0]:
            raise ConnectionError("WebSocket upgrade refused")
        self.rest = buf.split(b"\r\n\r\n", 1)[1]
        self.next_id = 0
        self.events = []

    def _read(self, n: int) -> bytes:
        while len(self.rest) < n:
            chunk = self.sock.recv(max(65536, n - len(self.rest)))
            if not chunk:
                raise ConnectionError("Chrome closed the connection")
            self.rest += chunk
        out, self.rest = self.rest[:n], self.rest[n:]
        return out

    def _send_frame(self, opcode: int, payload: bytes):
        head = bytes([0x80 | opcode])
        n = len(payload)
        if n < 126:
            head += bytes([0x80 | n])
        elif n < 65536:
            head += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            head += bytes([0x80 | 127]) + struct.pack(">Q", n)
        mask = os.urandom(4)
        self.sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

    def _recv_message(self) -> str:
        data = b""
        while True:
            b0, b1 = self._read(2)
            opcode, n = b0 & 0x0F, b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read(8))[0]
            mask = self._read(4) if b1 & 0x80 else None
            payload = self._read(n)
            if mask:
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            if opcode == 0x9:
                self._send_frame(0xA, payload)
                continue
            if opcode == 0x8:
                raise ConnectionError("Chrome closed the WebSocket")
            if opcode in (0x0, 0x1, 0x2):
                data += payload
                if b0 & 0x80:
                    return data.decode("utf-8", "replace")

    def call(self, method: str, params=None, session=None, timeout: float = 30.0):
        self.next_id += 1
        mid = self.next_id
        msg = {"id": mid, "method": method, "params": params or {}}
        if session:
            msg["sessionId"] = session
        self._send_frame(0x1, json.dumps(msg).encode())
        deadline = time.time() + timeout
        while time.time() < deadline:
            m = json.loads(self._recv_message())
            if m.get("id") == mid:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error'].get('message')}")
                return m.get("result", {})
            self.events.append(m)
        raise TimeoutError(method)

    def wait_event(self, name: str, session=None, timeout: float = 20.0) -> bool:
        deadline = time.time() + timeout
        while True:
            for i, e in enumerate(self.events):
                if e.get("method") == name and (session is None or e.get("sessionId") == session):
                    del self.events[:i + 1]
                    return True
            if time.time() >= deadline:
                return False
            self.sock.settimeout(max(0.1, deadline - time.time()))
            try:
                self.events.append(json.loads(self._recv_message()))
            except (socket.timeout, TimeoutError):
                return False
            finally:
                self.sock.settimeout(30.0)

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


def launch(chrome: str):
    profile = tempfile.mkdtemp(prefix="human-design-")
    cmd = [chrome, "--headless=new", "--remote-debugging-port=0", f"--user-data-dir={profile}", "--no-first-run",
           "--no-default-browser-check", "--hide-scrollbars", "--disable-gpu", "--mute-audio",
           "--disable-background-networking", "--disable-extensions", "about:blank"]
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)
    found = {}

    def reader():
        for raw in proc.stderr:
            line = raw.decode("utf-8", "replace")
            m = re.search(r"DevTools listening on (ws://\S+)", line)
            if m:
                found["url"] = m.group(1)
                break
        for _ in proc.stderr:  # keep draining so Chrome never blocks on a full pipe
            pass

    threading.Thread(target=reader, daemon=True).start()
    deadline = time.time() + 20
    while "url" not in found and time.time() < deadline and proc.poll() is None:
        time.sleep(0.05)
    if "url" not in found:
        proc.kill()
        shutil.rmtree(profile, ignore_errors=True)
        raise RuntimeError("Chrome did not start its DevTools endpoint")
    return proc, profile, found["url"]


def to_url(target: str) -> str:
    if re.match(r"^[a-z][a-z0-9+.-]*://", target, re.I):
        return target
    path = os.path.abspath(target)
    if not os.path.exists(path):
        sys.exit(f"not found: {target}")
    return "file://" + urllib.parse.quote(path)


def capture(cdp, session, url, width, scheme, a, out_dir, stem):
    height = 844 if width <= 600 else (1024 if width <= 1000 else 900)
    cdp.call("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": a.scale,
                                                     "mobile": width <= 600}, session)
    cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-color-scheme", "value": scheme},
                                                          {"name": "prefers-reduced-motion", "value": "no-preference"}]}, session)
    cdp.events.clear()
    cdp.call("Page.navigate", {"url": url}, session)
    loaded = cdp.wait_event("Page.loadEventFired", session, timeout=a.timeout)
    time.sleep(a.wait / 1000)
    res = cdp.call("Runtime.evaluate", {"expression": f"window.__hdW = {int(width)};" + MEASURE, "awaitPromise": True,
                                        "returnByValue": True}, session, timeout=40)
    if "exceptionDetails" in res:
        raise RuntimeError("measurement failed: " + str(res["exceptionDetails"].get("text")))
    facts = json.loads(res["result"]["value"])
    facts.update({"width": width, "scheme": scheme, "loaded": loaded})
    # animations that survive reduced motion
    cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-color-scheme", "value": scheme},
                                                          {"name": "prefers-reduced-motion", "value": "reduce"}]}, session)
    time.sleep(0.25)
    r2 = cdp.call("Runtime.evaluate", {"expression": "document.getAnimations ? document.getAnimations().filter(a => a.playState === 'running' "
                                                     "&& a.effect && a.effect.getTiming().duration > 20).length : 0", "returnByValue": True}, session)
    facts["animationsUnderReducedMotion"] = r2.get("result", {}).get("value", 0)
    cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-color-scheme", "value": scheme},
                                                          {"name": "prefers-reduced-motion", "value": "no-preference"}]}, session)
    shots = []
    if out_dir:
        full_h = height if a.fold else min(int(facts.get("pageHeight") or height), a.max_height)
        clip = {"x": 0, "y": 0, "width": width, "height": full_h, "scale": 1}
        png = cdp.call("Page.captureScreenshot", {"format": "png", "clip": clip, "captureBeyondViewport": True}, session, timeout=60)
        path = os.path.join(out_dir, f"{stem}-{width}-{scheme}.png")
        with open(path, "wb") as fh:
            fh.write(base64.b64decode(png["data"]))
        shots.append(path)
        if a.squint:
            cdp.call("Runtime.evaluate", {"expression": "document.documentElement.style.filter='blur(7px) grayscale(1)'"}, session)
            time.sleep(0.15)
            png = cdp.call("Page.captureScreenshot", {"format": "png", "clip": dict(clip, height=min(full_h, height * 2)),
                                                      "captureBeyondViewport": True}, session, timeout=60)
            path = os.path.join(out_dir, f"{stem}-{width}-{scheme}-squint.png")
            with open(path, "wb") as fh:
                fh.write(base64.b64decode(png["data"]))
            shots.append(path)
    facts["screenshots"] = shots
    return facts


def findings(f):
    """Turn measured facts into (severity, message) findings."""
    out = []
    for fam in f["families"]:
        if not fam["loaded"] and fam["share"] > 0.01:
            out.append(("error", f"Font \"{fam['name']}\" is declared for {fam['share']:.0%} of the text but did not load: the page shows a "
                                 "fallback. Load it (link or @font-face) or pick a face that is available."))
    real = [x for x in f["families"] if x["share"] > 0.02]
    if len(real) > 3:
        out.append(("warn", f"{len(real)} font families carry text ({', '.join(x['name'] for x in real)}). Two, or three with a mono, is the usual limit."))
    sizes = [s for s, share in f["sizes"] if share > 0.005]
    limit = 9 if f["width"] > 600 else 8
    if len(sizes) > limit:
        out.append(("warn", f"{len(sizes)} font sizes in use ({', '.join(f'{s:g}' for s in sizes)}px). A scale of 6 to 8 steps reads as a system; more reads as accident."))
    small = sum(share for s, share in f["sizes"] if s < 12)
    if small > 0.03:
        out.append(("warn", f"{small:.0%} of the text is under 12px."))
    if f["lowContrastCount"]:
        worst = f["lowContrast"][0]
        out.append(("error", f"{f['lowContrastCount']} text elements are under WCAG AA contrast, e.g. \"{worst['text']}\" "
                             f"({worst['fg']} on {worst['bg']}, {worst['ratio']}:1, needs {worst['need']}:1)."))
    if f["overImage"]:
        out.append(("look", f"{len(f['overImage'])}+ text elements sit on an image or gradient (e.g. \"{f['overImage'][0]['text']}\"): "
                            "contrast cannot be measured there; check the screenshot."))
    long_lines = [m for m in f["measures"] if m["cpl"] > 85]
    short_lines = [m for m in f["measures"] if m["cpl"] < 35 and f["width"] > 600]
    if long_lines:
        out.append(("warn", f"Running text is too wide: about {max(m['cpl'] for m in long_lines)} characters per line in {long_lines[0]['el']} "
                            "(aim for 45 to 75)."))
    squeezed = [m for m in f["measures"] if m["cpl"] < 25]
    if squeezed:
        out.append(("warn", f"Running text in {squeezed[0]['el']} is squeezed to about {squeezed[0]['cpl']} characters per line at {f['width']}px: "
                            "the columns did not collapse. Stack them at this width."))
    elif short_lines:
        out.append(("info", f"Running text in {short_lines[0]['el']} runs about {short_lines[0]['cpl']} characters per line: narrow for a desktop column."))
    tight = [m for m in f["measures"] if m.get("line") and m["line"] < 1.3 and m["size"] <= 20]
    if tight:
        out.append(("warn", f"Body text line height is {tight[0]['line']} in {tight[0]['el']}; running text usually needs 1.4 to 1.6."))
    if f["overflowX"]:
        out.append(("error", f"The page scrolls sideways by {f['overflowX']}px at {f['width']}px wide (" + "; ".join(f["overflowers"][:3]) + ")."))
    if f["clipped"]:
        out.append(("warn", f"Text may be clipped in {len(f['clipped'])} places, e.g. {f['clipped'][0]['el']} \"{f['clipped'][0]['text']}\"."))
    if f["centeredShare"] > 0.6 and f["chars"] > 300:
        out.append(("warn", f"{f['centeredShare']:.0%} of the text is centred. Centred everything is a template tell; align to an edge "
                            "and centre only short, isolated lines."))
    if f["spacing"]["offGridShare"] > 0.25 and f["spacing"]["distinct"] > 10:
        vals = ", ".join(f"{k:g}px" for k, _n in f["spacing"]["offGrid"][:5])
        out.append(("warn", f"{f['spacing']['offGridShare']:.0%} of paddings and gaps are off the 4px grid ({vals}); {f['spacing']['distinct']} "
                            "distinct values. Use the spacing tokens."))
    radii = f["radii"]
    total_r = sum(n for _k, n in radii) or 1
    if radii and radii[0][1] / total_r > 0.8 and total_r >= 12 and radii[0][0] not in ("pill",) and float(re.sub(r"[^0-9.]", "", radii[0][0]) or 0) >= 8:
        out.append(("info", f"One radius ({radii[0][0]}) on {radii[0][1]} of {total_r} rounded boxes. Uniform large rounding on everything is a "
                            "generator default: vary radius by role, or make the choice deliberate in the identity."))
    if len(radii) > 5:
        out.append(("warn", f"{len(radii)} distinct corner radii. Three is usually enough."))
    if f["shadows"] > 4:
        out.append(("warn", f"{f['shadows']} distinct shadows. Define two or three elevations."))
    if f["gradients"] >= 3 or f["gradientText"]:
        out.append(("info", f"{f['gradients']} gradient fills" + (f" and {f['gradientText']} gradient-clipped text" if f["gradientText"] else "")
                    + ". Gradients need a reason from the subject; decoration by gradient is the first AI tell people name."))
    if f["backdropBlur"] >= 3:
        out.append(("info", f"{f['backdropBlur']} blurred glass layers. On the web this is decoration unless content really scrolls under them."))
    if f["smallTargets"]:
        out.append(("error", f"{len(f['smallTargets'])}+ controls are under 24x24px (WCAG 2.2 target size): " + ", ".join(f["smallTargets"][:4]) + "."))
    if f["crampedTargets"]:
        out.append(("warn", f"{len(f['crampedTargets'])}+ controls are under 44px on a phone width: " + ", ".join(f["crampedTargets"][:4]) + "."))
    im = f["images"]
    if im["broken"]:
        out.append(("error", f"{im['broken']} images failed to load."))
    if im["noAlt"]:
        out.append(("warn", f"{im['noAlt']} images have no alt attribute (use alt=\"\" for decoration)."))
    if im["noSize"]:
        out.append(("info", f"{im['noSize']} images have no width and height: the layout will shift as they load."))
    h = f["headings"]
    if h["h1"] != 1 and h["total"]:
        out.append(("warn", f"{h['h1']} h1 elements; a page has one."))
    if h["skips"]:
        out.append(("info", f"Heading levels skip {h['skips']} time(s)."))
    if f["animationsUnderReducedMotion"]:
        out.append(("warn", f"{f['animationsUnderReducedMotion']} animations keep running under prefers-reduced-motion."))
    if f["infinite"] >= 3:
        out.append(("info", f"{f['infinite']} endless animations. Ambient motion competes with content; keep one at most."))
    if f["fold"]["controls"] > 12 and f["width"] > 600 and f["fold"]["largest"] and f["fold"]["largest"]["size"] >= 40:
        out.append(("info", f"{f['fold']['controls']} controls on the first screen of what looks like a marketing page. What is the one action?"))
    if not f["loaded"]:
        out.append(("warn", "The page did not fire its load event in time; results may be partial."))
    return out


def render(f, out):
    rank = {"error": 0, "warn": 1, "look": 2, "info": 3}
    o = [f"## {f['width']}px, {f['scheme']}", ""]
    if f["screenshots"]:
        o += ["Screenshots: " + ", ".join(f"`{p}`" for p in f["screenshots"]), ""]
    fams = ", ".join(f"{x['name']} {x['share']:.0%}" + ("" if x["loaded"] else " (NOT LOADED)") for x in f["families"] if x["share"] > 0.01)
    sizes = ", ".join(f"{s:g}" for s, share in f["sizes"] if share > 0.005)
    big = f["fold"]["largest"]
    o += [f"- Type: {fams}. Sizes (px): {sizes}. Weights: " + ", ".join(k for k, share in f["weights"] if share > 0.01) + ".",
          f"- Text colours: {f['textColorCount']} ({', '.join(k for k, _s in f['textColors'][:6])}). Backgrounds: {', '.join(f['backgrounds'][:5])}.",
          f"- Layout: {f['centeredShare']:.0%} of text centred; {f['spacing']['distinct']} spacing values, {f['spacing']['offGridShare']:.0%} off the 4px grid; "
          f"radii {', '.join(f'{k} x{n}' for k, n in f['radii'][:4]) or 'none'}; {f['shadows']} shadows; {f['gradients']} gradients.",
          f"- First screen: largest text {big['size']:g}px \"{big['text'][:60]}\"; {f['fold']['controls']} controls. Page height {f['pageHeight']}px."
          if big else f"- First screen: no text found. Page height {f['pageHeight']}px.",
          f"- Running text: " + (", ".join(f"{m['cpl']} cpl at {m['size']:g}px" for m in f["measures"][:4]) or "no paragraph long enough to measure") + ".", ""]
    for sev, msg in sorted(out, key=lambda x: rank[x[0]]):
        o.append(f"- **{sev}** {msg}")
    if not out:
        o.append("- No measured problems. Now open the screenshots and judge what a ruler cannot (references/critique.md).")
    return "\n".join(o)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="a local HTML file or a URL (for example a dev server on localhost)")
    ap.add_argument("--out", help="folder for screenshots (created when missing)")
    ap.add_argument("--widths", default="390,1440", help="comma-separated viewport widths, default 390,1440")
    ap.add_argument("--schemes", default="light", help="light, dark or light,dark")
    ap.add_argument("--fold", action="store_true", help="capture only the first screen")
    ap.add_argument("--squint", action="store_true", help="also save a blurred greyscale screenshot")
    ap.add_argument("--scale", type=float, default=1.0, help="device scale factor for screenshots (default 1)")
    ap.add_argument("--max-height", type=int, default=6000, help="tallest full-page screenshot in px")
    ap.add_argument("--wait", type=int, default=600, help="ms to wait after load before measuring")
    ap.add_argument("--timeout", type=float, default=20.0, help="seconds to wait for the page to load")
    ap.add_argument("--chrome", help="path to Chrome, Chromium or Edge when it is not in a standard location")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    chrome = find_chrome(a.chrome)
    if not chrome:
        sys.exit("No Chrome, Chromium or Edge found. Install one or pass --chrome PATH. Without a browser, open the page yourself, "
                 "take screenshots at 390 and 1440 wide, and go through references/critique.md by eye.")
    url = to_url(a.target)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", os.path.splitext(os.path.basename(urllib.parse.urlsplit(url).path))[0] or "page").strip("-") or "page"
    if a.out:
        os.makedirs(a.out, exist_ok=True)
    proc, profile, ws = launch(chrome)
    results = []
    try:
        cdp = CDP(ws)
        target = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        session = cdp.call("Target.attachToTarget", {"targetId": target, "flatten": True})["sessionId"]
        cdp.call("Page.enable", {}, session)
        cdp.call("Runtime.enable", {}, session)
        for width in [int(w) for w in a.widths.split(",") if w.strip()]:
            for scheme in [s.strip() for s in a.schemes.split(",") if s.strip()]:
                results.append(capture(cdp, session, url, width, scheme, a, a.out, stem))
        cdp.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)
    worst = 0
    if a.json:
        for f in results:
            f["findings"] = findings(f)
            worst = max([worst] + [2 for s, _ in f["findings"] if s == "error"])
        print(json.dumps(results, indent=1))
        return worst
    print(f"# Render check: {a.target}\n")
    for f in results:
        fs = findings(f)
        worst = max([worst] + [2 for s, _ in fs if s == "error"])
        print(render(f, fs) + "\n")
    print("Measured facts only. Open each screenshot and run the critique in references/critique.md: hierarchy, rhythm, "
          "alignment and character are judged by eye.")
    return worst


if __name__ == "__main__":
    sys.exit(main())
