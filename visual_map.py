#!/usr/bin/env python3
"""
Ventana "vim profile.yml" para el perfil de GitHub (estilo macu-dev):
  - izquierda: VISUAL.MAP (imágenes en 1 bit que se disuelven una en otra)
  - derecha:   profile.yml con números de línea y barra de estado NORMAL

Uso, desde la carpeta del repo ANTONIO30-09:
    pip install pillow opencv-python-headless    # opencv es opcional (centra la cara solo)
    python3 visual_map.py
    python3 visual_map.py --crop 100,50,700,800  # recorte manual de foto.png (x1,y1,x2,y2)

Imágenes (en orden):
    assets/foto.png                    -> tu foto (retrato)
    assets/visual-2.jpeg|png|jpg ...   -> logos/figuras (se ven completas)
"""
import glob
import html
import os
import re
import sys

from PIL import Image, ImageOps, ImageFilter, ImageStat

W, H = 300, 340
TARGET_PTS = 18000
SLOT = 7.0
LAYERS = 10
OUT = "assets/profile-window.svg"

BG = "#0D0D0D"
ROJO = "#8B0000"
ROJO_V = "#E63946"
ACENTO = "#FFD700"
GRIS = "#8A8A8A"
PALETA = {"g": "#FFD700", "r": "#E63946", "w": "#FFFFFF"}

# ── Contenido de profile.yml: (nivel, clave, valor) ──
YAML = [
    (0, "profile", None),
    (1, "subject", "Antonio Vicente García Corrales"),
    (1, "role", "Estudiante de Ingeniería de Sistemas"),
    (1, "origin", "Bolivia"),
    (1, "focus", "Machine Learning · IA Generativa · Full Stack"),
    (1, "status", "6to semestre · Buscando prácticas / Junior"),
    (1, "toolchain", "Python · FastAPI · React · TypeScript"),
    (0, "stack", None),
    (1, "languages", "Python · TypeScript · JavaScript · SQL · C# · C++"),
    (1, "ml_ia", "Machine Learning · IA Generativa"),
    (1, "backend", "FastAPI · SQL"),
    (1, "frontend", "React · TypeScript"),
    (1, "os", "Linux Mint · Bash"),
    (0, "contact", None),
    (1, "email", "antoniovicentegarciacorrales2@gmail.com"),
    (1, "instagram", "@ant_nin_o"),
    (1, "github", "ANTONIO30-09"),
    (1, "modalidad", "Remoto · Híbrido"),
]
HANDLE = "@ANTONIO30-09"

# Geometría
WIN_W = 900
CW, CH = 330, 436            # panel VISUAL.MAP
IX, IY = 15, 54              # imagen dentro del panel
PX, PY = 16, 56              # panel izquierdo en la ventana
RX, RY = 362, 56             # panel derecho
RW, RH = 522, 436
WIN_H = PY + CH + 16


# ───────────────────────── imágenes ─────────────────────────
def find_sources():
    files = []
    if os.path.exists("assets/foto.png"):
        files.append(("assets/foto.png", "cover"))
    extra = []
    for ext in ("png", "jpg", "jpeg", "webp"):
        extra += glob.glob(f"assets/visual-*.{ext}")
    files += [(f, "contain") for f in sorted(extra)]
    return files


def parse_crop():
    if "--crop" in sys.argv:
        try:
            v = sys.argv[sys.argv.index("--crop") + 1]
            a = [int(t) for t in v.split(",")]
            if len(a) == 4:
                return tuple(a)
        except Exception:
            print("Formato de --crop: x1,y1,x2,y2")
    return None


def detect_face_crop(img_l):
    """Recorte centrado en la cara con OpenCV (si está instalado)."""
    try:
        import cv2
        import numpy as np
    except Exception:
        print("  (tip: pip install opencv-python-headless para centrar la cara automáticamente)")
        return None
    arr = np.array(img_l)
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    caras = casc.detectMultiScale(arr, 1.1, 5, minSize=(max(40, img_l.width // 12),) * 2)
    if len(caras) == 0:
        return None
    x, y, fw, fh = max(caras, key=lambda f: f[2] * f[3])
    w, h = img_l.size
    ratio = W / H
    ch = fh * 3.4
    cw = ch * ratio
    if cw > w:
        cw, ch = w, w / ratio
    if ch > h:
        ch, cw = h, h * ratio
    cx, cy = x + fw / 2, y + fh / 2 + fh * 0.35
    left = min(max(cx - cw / 2, 0), w - cw)
    top = min(max(cy - ch / 2, 0), h - ch)
    print("  cara detectada, recorte automático")
    return (int(left), int(top), int(left + cw), int(top + ch))


def prepare(path, mode):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        fondo = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(fondo, img)
    img = img.convert("L")

    if mode == "cover":
        box = parse_crop() or detect_face_crop(img)
        if box:
            img = img.crop(box)

    w, h = img.size
    ratio = W / H
    bw, bh = max(1, w // 20), max(1, h // 20)
    borde = [img.crop((0, 0, w, bh)), img.crop((0, h - bh, w, h)),
             img.crop((0, 0, bw, h)), img.crop((w - bw, 0, w, h))]
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
    else:
        escala = min(W * 0.92 / w, H * 0.92 / h)
        nw, nh = max(1, int(w * escala)), max(1, int(h * escala))
        img = img.resize((nw, nh), Image.LANCZOS)
        lienzo = Image.new("L", (W, H), 255 if invertir else 0)
        lienzo.paste(img, ((W - nw) // 2, (H - nh) // 2))
        img = lienzo

    if invertir:
        img = ImageOps.invert(img)
    img = ImageOps.autocontrast(img, cutoff=2)
    if mode == "cover":   # más contraste local para que la cara se note
        img = Image.blend(img, ImageOps.equalize(img), 0.55)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=140, threshold=2))
    return img, invertir


def dither(img, gamma):
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
    lo, hi = 0.1, 5.0
    best = None
    for _ in range(10):
        mid = (lo + hi) / 2
        pts = dither(img, mid)
        if best is None or abs(len(pts) - TARGET_PTS) < abs(len(best) - TARGET_PTS):
            best = pts
        if len(pts) > TARGET_PTS:
            lo = mid
        else:
            hi = mid
    return best


def kf(name, puntos):
    vistos, partes = set(), []
    for p, o in puntos:
        key = round(p, 3)
        if key in vistos:
            continue
        vistos.add(key)
        partes.append(f"{key}%{{opacity:{o}}}")
    return f"@keyframes {name}{{{''.join(partes)}}}"


def layer_keyframes(name, s, slot, l):
    k = LAYERS - 1
    in_s = s + slot * (0.30 * l / k)
    in_e = in_s + slot * 0.12
    out_s = s + slot * (0.70 + 0.18 * l / k)
    out_e = out_s + slot * 0.12
    return kf(name, [(0, 0), (in_s, 0), (in_e, 1), (out_s, 1), (out_e, 0), (100, 0)])


# ───────────────────────── panel izquierdo ─────────────────────────
def build_visual_panel(sources):
    n = len(sources)
    total = SLOT * n
    slot = 100.0 / n
    css, frames = [], []
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
        tn = f"t{i}"
        css.append(kf(tn, [(0, 0), (s + slot * 0.10, 0), (s + slot * 0.30, 1), (s + slot * 0.75, 1),
                           (s + slot * 0.95, 0), (100, 0)]) + f".{tn}{{opacity:0;animation:{tn} {total}s linear infinite}}")
        g.append(f'<g class="{tn}">')
        g.append(f'<text x="{IX}" y="{CH - 14}" fill="{GRIS}" font-size="10">PTS {len(pts)} · FS/SERPENTINE</text>')
        g.append(f'<text x="{CW - IX}" y="{CH - 14}" fill="{GRIS}" font-size="10" text-anchor="end">FRAME {i + 1}/{n}</text>')
        g.append("</g>")
        frames.append("\n".join(g))

    br = (f'<path d="M7 60V46H21 M{CW - 21} 46H{CW - 7}V60 M7 {CH - 48}V{CH - 34}H21 '
          f'M{CW - 21} {CH - 34}H{CW - 7}V{CH - 48}" fill="none" stroke="{ROJO}" stroke-width="2"/>')
    panel = f"""<g transform="translate({PX},{PY})">
<rect x="1" y="1" width="{CW - 2}" height="{CH - 2}" rx="12" fill="{BG}" stroke="{ROJO}" stroke-width="2"/>
<path d="M1 13a12 12 0 0 1 12-12h{CW - 26}a12 12 0 0 1 12 12v27H1z" fill="#1A0000"/>
<text x="16" y="25" fill="{ACENTO}" font-size="13" font-weight="700" letter-spacing="1.5">VISUAL.MAP</text>
<text x="{CW - 15}" y="25" fill="{GRIS}" font-size="10" text-anchor="end">{W}×{H} / 1-BIT</text>
{br}
{chr(10).join(frames)}
</g>"""
    return panel, css


# ───────────────────────── panel derecho (vim) ─────────────────────────
def value_tspans(v):
    partes = [html.escape(p) for p in v.split(" · ")]
    sep = f'<tspan fill="{GRIS}"> · </tspan>'
    return sep.join(f'<tspan fill="#FFFFFF">{p}</tspan>' for p in partes)


def build_yaml_panel():
    texto = "\n".join(("  " * lv) + k + ":" + (f" {v}" if v else "") for lv, k, v in YAML) + "\n"
    nlines = len(YAML)
    nbytes = len(texto.encode("utf-8"))
    LH, Y0 = 17.5, 66
    out = []
    for i, (lv, k, v) in enumerate(YAML):
        y = Y0 + i * LH
        x = 58 + lv * 16
        delay = 0.4 + i * 0.12
        kc = ACENTO if lv == 0 else ROJO_V
        w = "700" if lv == 0 else "400"
        val = f'<tspan fill="#FFFFFF" xml:space="preserve"> </tspan>{value_tspans(v)}' if v else ""
        out.append(
            f'<g class="ln" style="animation-delay:{delay:.2f}s">'
            f'<text x="42" y="{y:.1f}" fill="#555555" font-size="11.5" text-anchor="end">{i + 1}</text>'
            f'<text x="{x}" y="{y:.1f}" font-size="12.5" xml:space="preserve">'
            f'<tspan fill="{kc}" font-weight="{w}">{html.escape(k)}:</tspan>{val}</text></g>'
        )
    cy = Y0 + (nlines - 1) * LH
    cursor = f'<rect class="cur" x="58" y="{cy - 12:.1f}" width="7.5" height="15" fill="{ACENTO}"/>'
    sy = RH - 38
    panel = f"""<g transform="translate({RX},{RY})">
<rect x="1" y="1" width="{RW - 2}" height="{RH - 2}" rx="12" fill="{BG}" stroke="{ROJO}" stroke-width="2"/>
<path d="M1 13a12 12 0 0 1 12-12h{RW - 26}a12 12 0 0 1 12 12v27H1z" fill="#1A0000"/>
<text x="18" y="25" fill="#FFFFFF" font-size="13" font-weight="700">profile.yml<tspan fill="{GRIS}" font-size="10" font-weight="400" dx="3">[YAML]</tspan></text>
<rect x="{RW - 18 - 150}" y="8" width="150" height="25" rx="12.5" fill="#2A0000" stroke="{ROJO}"/>
<text x="{RW - 18 - 75}" y="24.5" fill="{ACENTO}" font-size="11.5" font-weight="700" text-anchor="middle">{HANDLE}</text>
{chr(10).join(out)}
{cursor}
<line x1="1" y1="{sy}" x2="{RW - 1}" y2="{sy}" stroke="#3A1010"/>
<rect x="14" y="{sy + 8}" width="64" height="22" rx="4" fill="{ACENTO}"/>
<text x="46" y="{sy + 23.5}" fill="#0D0D0D" font-size="11" font-weight="700" text-anchor="middle">NORMAL</text>
<text x="94" y="{sy + 23.5}" fill="#FFFFFF" font-size="12" font-weight="700">profile.yml</text>
<text x="{RW / 2 + 40}" y="{sy + 23.5}" fill="{GRIS}" font-size="11" text-anchor="middle">[utf-8]</text>
<text x="{RW - 16}" y="{sy + 23.5}" fill="{GRIS}" font-size="11" text-anchor="end">{nlines}L, {nbytes}B 100% {nlines}:1</text>
</g>"""
    return panel


def main():
    sources = find_sources()
    if not sources:
        sys.exit("No encuentro assets/foto.png. Ejecuta el script dentro de ~/ANTONIO30-09")
    print(f"Imágenes: {len(sources)}")
    left, css_left = build_visual_panel(sources)
    right = build_yaml_panel()

    css = [
        "text{font-family:'Fira Code','DejaVu Sans Mono',monospace}",
        ".ln{opacity:0;animation:show .01s forwards}",
        "@keyframes show{to{opacity:1}}",
        ".cur{animation:blink 1s steps(1) infinite}",
        "@keyframes blink{50%{opacity:0}}",
    ] + css_left

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIN_W}" height="{WIN_H}" viewBox="0 0 {WIN_W} {WIN_H}">
<style>{''.join(css)}</style>
<rect x="1" y="1" width="{WIN_W - 2}" height="{WIN_H - 2}" rx="16" fill="#080808" stroke="{ROJO}" stroke-width="2"/>
<circle cx="30" cy="28" r="6" fill="{ROJO}"/>
<circle cx="52" cy="28" r="6" fill="{ACENTO}"/>
<circle cx="74" cy="28" r="6" fill="#FFFFFF"/>
<text x="{WIN_W / 2}" y="32" fill="{GRIS}" font-size="12" text-anchor="middle">vim profile.yml</text>
{left}
{right}
</svg>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Listo: {OUT} ({os.path.getsize(OUT) // 1024} KB)")

    if os.path.exists("README.md"):
        md = open("README.md", encoding="utf-8").read()
        bloque = f'<div align="center">\n  <img src="assets/profile-window.svg" width="{WIN_W}" alt="vim profile.yml" />\n</div>'
        if "assets/profile-window.svg" in md:
            print("README.md ya usa la ventana")
        else:
            new = re.sub(r"<table>.*?</table>", bloque, md, count=1, flags=re.S)
            if new != md:
                open("README.md", "w", encoding="utf-8").write(new)
                print("README.md actualizado (la tabla de foto + whoami se reemplazó)")
            else:
                print("No encontré la <table> en README.md; pon este bloque en la sección whoami:\n" + bloque)


if __name__ == "__main__":
    main()
