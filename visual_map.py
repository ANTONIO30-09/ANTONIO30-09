#!/usr/bin/env python3
"""
Efecto VISUAL.MAP (1-bit, Floyd-Steinberg serpentine) con desvanecimiento por puntos.

Uso, desde la carpeta del repo ANTONIO30-09:
    pip install pillow            # solo la primera vez
    python3 visual_map.py

Imágenes (en este orden):
    assets/foto.png                      -> tu foto (recorte tipo retrato)
    assets/visual-2.jpeg|png|jpg ...     -> logos/figuras (se ven completas)
Cada imagen se disuelve punto por punto, se apaga y da paso a la siguiente.
"""
import glob
import os
import re
import sys

from PIL import Image, ImageOps, ImageFilter, ImageStat

W, H = 300, 340
TARGET_PTS = 18000
SLOT = 7.0               # segundos por imagen
LAYERS = 10              # capas de puntos que se encienden/apagan escalonadas
OUT = "assets/visual-map.svg"

BG = "#0D0D0D"
ROJO = "#8B0000"
ACENTO = "#FFD700"
PALETA = {"g": "#FFD700", "r": "#E63946", "w": "#FFFFFF"}

CW, CH = 330, 436
IX, IY = 15, 54


def find_sources():
    files = []
    if os.path.exists("assets/foto.png"):
        files.append(("assets/foto.png", "cover"))
    extra = []
    for ext in ("png", "jpg", "jpeg", "webp"):
        extra += glob.glob(f"assets/visual-*.{ext}")
    files += [(f, "contain") for f in sorted(extra)]
    return files


def prepare(path, mode):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        fondo = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(fondo, img)
    img = img.convert("L")
    w, h = img.size
    ratio = W / H

    # ¿fondo claro? -> se invierte para que el sujeto sea lo que se enciende
    borde = [img.crop((0, 0, w, max(1, h // 20))), img.crop((0, h - max(1, h // 20), w, h)),
             img.crop((0, 0, max(1, w // 20), h)), img.crop((w - max(1, w // 20), 0, w, h))]
    media = sum(ImageStat.Stat(b).mean[0] for b in borde) / 4
    invertir = media > 150

    if mode == "cover":
        if w / h > ratio:
            cw, ch = int(h * ratio), h
        else:
            cw, ch = w, int(w / ratio)
        left = (w - cw) // 2
        top = int((h - ch) * 0.25)
        img = img.crop((left, top, left + cw, top + ch)).resize((W, H), Image.LANCZOS)
    else:  # contain: figura completa con margen
        escala = min(W * 0.92 / w, H * 0.92 / h)
        nw, nh = max(1, int(w * escala)), max(1, int(h * escala))
        img = img.resize((nw, nh), Image.LANCZOS)
        lienzo = Image.new("L", (W, H), 255 if invertir else 0)
        lienzo.paste(img, ((W - nw) // 2, (H - nh) // 2))
        img = lienzo

    if invertir:
        img = ImageOps.invert(img)
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=2))
    return img, invertir


def dither(img, gamma):
    """Floyd-Steinberg serpentine. Devuelve los puntos encendidos."""
    px = img.load()
    rows = [[(px[x, y] / 255.0) ** gamma for x in range(W)] for y in range(H)]
    lit = []
    for y in range(H):
        ltr = (y % 2 == 0)
        xs = range(W) if ltr else range(W - 1, -1, -1)
        d = 1 if ltr else -1
        row = rows[y]
        nxt = rows[y + 1] if y + 1 < H else None
        for x in xs:
            old = row[x]
            new = 1.0 if old >= 0.5 else 0.0
            if new:
                lit.append((x, y))
            err = old - new
            xn = x + d
            if 0 <= xn < W:
                row[xn] += err * 7 / 16
            if nxt is not None:
                xb = x - d
                if 0 <= xb < W:
                    nxt[xb] += err * 3 / 16
                nxt[x] += err * 5 / 16
                if 0 <= xn < W:
                    nxt[xn] += err * 1 / 16
    return lit


def fit_points(img):
    """Gamma que deja ~TARGET_PTS puntos (si la imagen tiene menos, usa los que haya)."""
    lo, hi = 0.25, 5.0
    best = None
    for _ in range(9):
        mid = (lo + hi) / 2
        pts = dither(img, mid)
        if best is None or abs(len(pts) - TARGET_PTS) < abs(len(best) - TARGET_PTS):
            best = pts
        if len(pts) > TARGET_PTS:
            lo = mid
        else:
            hi = mid
    return best


def layer_keyframes(name, s, slot, l):
    """Cada capa se enciende y se apaga en momentos distintos -> efecto de disolución."""
    k = LAYERS - 1
    in_s = s + slot * (0.30 * l / k)
    in_e = in_s + slot * 0.12
    out_s = s + slot * (0.70 + 0.18 * l / k)
    out_e = out_s + slot * 0.12
    puntos = [(0, 0), (in_s, 0), (in_e, 1), (out_s, 1), (out_e, 0), (100, 0)]
    vistos, partes = set(), []
    for p, o in puntos:
        key = round(p, 3)
        if key in vistos:
            continue
        vistos.add(key)
        partes.append(f"{key}%{{opacity:{o}}}")
    return f"@keyframes {name}{{{''.join(partes)}}}"


def main():
    sources = find_sources()
    if not sources:
        sys.exit("No encuentro assets/foto.png. Ejecuta el script dentro de ~/ANTONIO30-09")
    n = len(sources)
    total = SLOT * n
    slot = 100.0 / n
    print(f"Imágenes: {n}")

    css = [
        "text{font-family:'Fira Code','DejaVu Sans Mono',monospace}",
        ".hd{animation:hd 3s steps(1) infinite}",
        "@keyframes hd{50%{opacity:.35}}",
    ]
    frames = []
    for i, (src, mode) in enumerate(sources):
        img, inv = prepare(src, mode)
        pts = fit_points(img)
        print(f"  {src} [{mode}{', invertida' if inv else ''}]: {len(pts)} puntos")
        s = i * slot

        capas = {l: {"g": [], "r": [], "w": []} for l in range(LAYERS)}
        for x, y in pts:
            c = (x * 7 + y * 13) % 10
            c = "g" if c < 6 else ("r" if c < 8 else "w")
            l = ((x * 73856093) ^ (y * 19349663)) % LAYERS
            capas[l][c].append(f"M{x + IX} {y + IY}h1v1h-1z")

        g = []
        for l in range(LAYERS):
            nombre = f"l{i}_{l}"
            css.append(layer_keyframes(nombre, s, slot, l))
            css.append(f".{nombre}{{opacity:0;animation:{nombre} {total}s linear infinite}}")
            g.append(f'<g class="{nombre}">')
            for c, segs in capas[l].items():
                if segs:
                    g.append(f'<path d="{"".join(segs)}" fill="{PALETA[c]}" fill-opacity="0.92"/>')
            g.append("</g>")

        # texto del pie: se desvanece con la imagen
        tn = f"t{i}"
        pts_t = [(0, 0), (s + slot * 0.10, 0), (s + slot * 0.30, 1), (s + slot * 0.75, 1), (s + slot * 0.95, 0), (100, 0)]
        vistos, partes = set(), []
        for p, o in pts_t:
            key = round(p, 3)
            if key in vistos:
                continue
            vistos.add(key)
            partes.append(f"{key}%{{opacity:{o}}}")
        css.append(f"@keyframes {tn}{{{''.join(partes)}}}.{tn}{{opacity:0;animation:{tn} {total}s linear infinite}}")
        g.append(f'<g class="{tn}">')
        g.append(f'<text x="{IX}" y="{CH - 14}" fill="#8A8A8A" font-size="10">PTS {len(pts)} · FS/SERPENTINE</text>')
        g.append(f'<text x="{CW - IX}" y="{CH - 14}" fill="#8A8A8A" font-size="10" text-anchor="end">FRAME {i + 1}/{n}</text>')
        g.append("</g>")
        frames.append("\n".join(g))

    br = (f'<path d="M7 60V46H21 M{CW - 21} 46H{CW - 7}V60 M7 {CH - 48}V{CH - 34}H21 '
          f'M{CW - 21} {CH - 34}H{CW - 7}V{CH - 48}" fill="none" stroke="{ROJO}" stroke-width="2"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}">
<style>{''.join(css)}</style>
<rect x="1" y="1" width="{CW - 2}" height="{CH - 2}" rx="14" fill="{BG}" stroke="{ROJO}" stroke-width="2"/>
<path d="M1 15a14 14 0 0 1 14-14h{CW - 30}a14 14 0 0 1 14 14v25H1z" fill="#1A0000"/>
<circle class="hd" cx="20" cy="21" r="4" fill="{ACENTO}"/>
<text x="32" y="25" fill="{ACENTO}" font-size="13" font-weight="700" letter-spacing="1.5">VISUAL.MAP</text>
<text x="{CW - 15}" y="25" fill="#8A8A8A" font-size="10" text-anchor="end">{W}×{H} / 1-BIT</text>
{br}
{chr(10).join(frames)}
</svg>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Listo: {OUT} ({os.path.getsize(OUT) // 1024} KB)")

    if os.path.exists("README.md"):
        md = open("README.md", encoding="utf-8").read()
        new = re.sub(r'<img src="assets/foto\.png"[^>]*/?>',
                     f'<img src="assets/visual-map.svg" width="{CW}" alt="VISUAL.MAP" />', md)
        new = re.sub(r'<td align="center" width="\d+">', '<td align="center" width="350">', new, count=1)
        if new != md:
            open("README.md", "w", encoding="utf-8").write(new)
            print("README.md actualizado")
        else:
            print("README.md ya estaba actualizado")


if __name__ == "__main__":
    main()
