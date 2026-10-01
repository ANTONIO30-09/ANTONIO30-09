#!/usr/bin/env python3
"""
Efecto VISUAL.MAP (1-bit, Floyd-Steinberg serpentine) para el perfil de GitHub.

Uso, desde la carpeta del repo ANTONIO30-09:
    pip install pillow            # solo la primera vez
    python3 visual_map.py

Fotos que usa (en este orden):
    assets/foto.png
    assets/visual-2.png, assets/visual-3.png, ...   (o .jpg / .jpeg)
Cada foto aparece con un barrido, se desvanece y da paso a la siguiente.

Crea assets/visual-map.svg y cambia la foto del README por ese SVG.
"""
import glob
import os
import re
import sys

from PIL import Image, ImageOps, ImageFilter

W, H = 300, 340          # tamaño de la imagen en puntos
TARGET_PTS = 18000       # puntos encendidos por foto
SLOT = 7.0               # segundos que dura cada foto
OUT = "assets/visual-map.svg"

BG = "#0D0D0D"
ROJO = "#8B0000"
ACENTO = "#FFD700"
PALETA = {"g": "#FFD700", "r": "#E63946", "w": "#FFFFFF"}

# Geometría de la tarjeta
CW, CH = 330, 436
IX, IY = 15, 54          # esquina superior izquierda de la imagen


def find_sources():
    files = []
    if os.path.exists("assets/foto.png"):
        files.append("assets/foto.png")
    extra = []
    for ext in ("png", "jpg", "jpeg", "webp"):
        extra += glob.glob(f"assets/visual-*.{ext}")
    files += sorted(extra)
    return files


def prepare(path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img).convert("L")
    # recorte centrado (un poco hacia arriba para no perder la cara)
    w, h = img.size
    ratio = W / H
    if w / h > ratio:
        cw, ch = int(h * ratio), h
    else:
        cw, ch = w, int(w / ratio)
    left = (w - cw) // 2
    top = int((h - ch) * 0.25)
    img = img.crop((left, top, left + cw, top + ch)).resize((W, H), Image.LANCZOS)
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=2))
    return img


def dither(img, gamma):
    """Floyd-Steinberg en recorrido serpentine. Devuelve lista de (x, y) encendidos."""
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
    """Busca el gamma que deja ~TARGET_PTS puntos encendidos."""
    lo, hi = 0.25, 5.0
    best = None
    for _ in range(9):
        mid = (lo + hi) / 2
        pts = dither(img, mid)
        if best is None or abs(len(pts) - TARGET_PTS) < abs(len(best) - TARGET_PTS):
            best = pts
        if len(pts) > TARGET_PTS:
            lo = mid      # demasiados -> oscurecer
        else:
            hi = mid
    return best


def build_paths(points):
    base = {"g": [], "r": [], "w": []}
    tw = {0: [], 1: [], 2: []}
    for x, y in points:
        k = (x * 7 + y * 13) % 10
        c = "g" if k < 6 else ("r" if k < 8 else "w")
        seg = f"M{x + IX} {y + IY}h1v1h-1z"
        base[c].append(seg)
        h = (x * 31 + y * 17) % 40
        if h < 3:
            tw[h].append(seg)
    return base, tw


def keyframes(i, n):
    s = i * 100.0 / n
    a = s + 0.35 * 100.0 / n      # fin del barrido
    f = s + 0.85 * 100.0 / n      # empieza el desvanecimiento
    e = s + 100.0 / n
    p = lambda v: f"{v:.3f}%"
    eps = 0.01

    # opacidad del grupo
    op = []
    if s > 0:
        op += [f"0%{{opacity:0}}", f"{p(s - eps)}{{opacity:0}}"]
    op += [f"{p(s)}{{opacity:1}}", f"{p(f)}{{opacity:1}}", f"{p(e)}{{opacity:0}}"]
    if e < 100:
        op += ["100%{opacity:0}"]

    # cortina que descubre la imagen de arriba hacia abajo
    cv = ["0%{transform:scaleY(1)}"]
    if s > 0:
        cv.append(f"{p(s)}{{transform:scaleY(1)}}")
    cv += [f"{p(a)}{{transform:scaleY(0)}}", "100%{transform:scaleY(0)}"]

    # línea de escaneo
    sc = ["0%{opacity:0;transform:translateY(0)}"]
    if s > 0:
        sc.append(f"{p(s - eps)}{{opacity:0;transform:translateY(0)}}")
    sc += [
        f"{p(s)}{{opacity:1;transform:translateY(0)}}",
        f"{p(a)}{{opacity:1;transform:translateY({H}px)}}",
        f"{p(a + eps)}{{opacity:0;transform:translateY({H}px)}}",
        "100%{opacity:0;transform:translateY(0)}",
    ]
    return (
        f"@keyframes op{i}{{{''.join(op)}}}"
        f"@keyframes cv{i}{{{''.join(cv)}}}"
        f"@keyframes sc{i}{{{''.join(sc)}}}"
    )


def main():
    sources = find_sources()
    if not sources:
        sys.exit("No encuentro assets/foto.png. Ejecuta el script dentro de ~/ANTONIO30-09")
    n = len(sources)
    total = SLOT * n
    print(f"Fotos: {n} -> {sources}")

    css = [
        "text{font-family:'Fira Code','DejaVu Sans Mono',monospace}",
        ".tw{animation:tw 2.4s ease-in-out infinite}",
        "@keyframes tw{0%,100%{opacity:0}50%{opacity:1}}",
        ".hd{animation:hd 3s steps(1) infinite}",
        "@keyframes hd{50%{opacity:.35}}",
    ]
    frames = []
    for i, src in enumerate(sources):
        img = prepare(src)
        pts = fit_points(img)
        base, tw = build_paths(pts)
        print(f"  {src}: {len(pts)} puntos")
        css.append(keyframes(i, n))
        css.append(
            f".o{i}{{animation:op{i} {total}s linear infinite}}"
            f".c{i}{{transform-origin:{IX}px {IY + H}px;animation:cv{i} {total}s linear infinite}}"
            f".s{i}{{animation:sc{i} {total}s linear infinite}}"
        )
        g = [f'<g class="o{i}" opacity="{1 if i == 0 else 0}">']
        for c, segs in base.items():
            if segs:
                g.append(f'<path d="{"".join(segs)}" fill="{PALETA[c]}" fill-opacity="0.92"/>')
        for k, segs in tw.items():
            if segs:
                g.append(
                    f'<path class="tw" d="{"".join(segs)}" fill="#FFFFFF" opacity="0" '
                    f'style="animation-delay:{k * 0.8:.1f}s"/>'
                )
        # cortina + línea de escaneo
        g.append(f'<rect class="c{i}" x="{IX}" y="{IY}" width="{W}" height="{H}" fill="{BG}"/>')
        g.append(f'<rect class="s{i}" x="{IX}" y="{IY}" width="{W}" height="2" fill="{ACENTO}"/>')
        g.append(
            f'<text x="{IX}" y="{CH - 14}" fill="#8A8A8A" font-size="10">'
            f'PTS {len(pts)} · FS/SERPENTINE</text>'
        )
        g.append(
            f'<text x="{CW - IX}" y="{CH - 14}" fill="#8A8A8A" font-size="10" text-anchor="end">'
            f'FRAME {i + 1}/{n}</text>'
        )
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

    # Cambiar la foto del README por el SVG animado
    if os.path.exists("README.md"):
        md = open("README.md", encoding="utf-8").read()
        new = md
        new = re.sub(r'<img src="assets/foto\.png"[^>]*/?>',
                     f'<img src="assets/visual-map.svg" width="{CW}" alt="VISUAL.MAP" />', new)
        new = re.sub(r'<td align="center" width="\d+">', '<td align="center" width="350">', new, count=1)
        if new != md:
            open("README.md", "w", encoding="utf-8").write(new)
            print("README.md actualizado")
        else:
            print("README.md ya estaba actualizado (o no tiene la etiqueta de la foto)")


if __name__ == "__main__":
    main()
