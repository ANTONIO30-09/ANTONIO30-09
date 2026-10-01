#!/usr/bin/env python3
"""
Genera el perfil de GitHub de Antonio (estilo terminal animado, como macu-dev).
Uso (desde la carpeta del repo ANTONIO30-09):
    python3 build_profile.py
Crea: assets/banner.svg, assets/whoami.svg, assets/radar.svg,
      assets/radar-langs.svg y README.md
"""
import math
import os

ROJO = "#8B0000"
ACENTO = "#FFD700"
FONDO = "#0D0D0D"
GRID = "#3A1010"
TEXTO = "#FFFFFF"

os.makedirs("assets", exist_ok=True)

# ───────────────────────── BANNER ANIMADO ─────────────────────────
BANNER = """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="240" viewBox="0 0 900 240">
  <defs>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#000000"/>
      <stop offset="0.4" stop-color="#8B0000"/>
      <stop offset="0.75" stop-color="#FFD700"/>
      <stop offset="1" stop-color="#FFFFFF"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0" r="0.9">
      <stop offset="0" stop-color="#8B0000" stop-opacity="0.55"/>
      <stop offset="1" stop-color="#0D0D0D" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#FFD700" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#FFD700" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#FFD700" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="clip"><rect width="900" height="240" rx="16"/></clipPath>
  </defs>
  <style>
    .name{font:700 66px 'Fira Code','DejaVu Sans Mono',monospace;fill:#FFFFFF;
          opacity:0;animation:rise 1s .2s ease-out forwards}
    .sub{font:400 30px 'Fira Code','DejaVu Sans Mono',monospace;fill:#FFD700;
         opacity:0;animation:rise 1s .6s ease-out forwards}
    .cmd{font:400 17px 'Fira Code','DejaVu Sans Mono',monospace;fill:#BBBBBB;
         opacity:0;animation:rise 1s 1.1s ease-out forwards}
    .cur{fill:#FFD700;animation:blink 1s steps(1) infinite}
    .dot{fill:#FFD700;opacity:.0;animation:float 6s ease-in-out infinite}
    .sweep{animation:slide 5s linear infinite}
    .scan{animation:scan 6s linear infinite}
    @keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
    @keyframes blink{50%{opacity:0}}
    @keyframes float{0%{opacity:0;transform:translateY(0)}30%{opacity:.7}100%{opacity:0;transform:translateY(-90px)}}
    @keyframes slide{from{transform:translateX(-300px)}to{transform:translateX(1000px)}}
    @keyframes scan{from{transform:translateY(-10px)}to{transform:translateY(250px)}}
  </style>
  <g clip-path="url(#clip)">
    <rect width="900" height="240" fill="#0D0D0D"/>
    <rect width="900" height="240" fill="url(#glow)"/>
    <rect class="scan" width="900" height="2" fill="#FFD700" opacity="0.08"/>
    <circle class="dot" cx="120" cy="200" r="3" style="animation-delay:0s"/>
    <circle class="dot" cx="300" cy="215" r="2" style="animation-delay:1.4s"/>
    <circle class="dot" cx="520" cy="205" r="3" style="animation-delay:2.6s"/>
    <circle class="dot" cx="700" cy="220" r="2" style="animation-delay:3.8s"/>
    <circle class="dot" cx="820" cy="200" r="3" style="animation-delay:4.6s"/>
    <rect y="226" width="900" height="14" fill="url(#bar)"/>
    <rect class="sweep" y="226" width="300" height="14" fill="url(#sweep)"/>
  </g>
  <rect x="1" y="1" width="898" height="238" rx="16" fill="none" stroke="#8B0000" stroke-width="2"/>
  <text class="name" x="450" y="105" text-anchor="middle">Antonio Vicente</text>
  <text class="sub" x="450" y="148" text-anchor="middle">García Corrales</text>
  <text class="cmd" x="450" y="196" text-anchor="middle">&gt; sistemas --ml --genai --fullstack<tspan class="cur"> █</tspan></text>
</svg>
"""
open("assets/banner.svg", "w", encoding="utf-8").write(BANNER)

# ───────────────────────── TERMINAL whoami ─────────────────────────
WHOAMI = """<svg xmlns="http://www.w3.org/2000/svg" width="620" height="270" viewBox="0 0 620 270">
  <style>
    text{font-family:'Fira Code','DejaVu Sans Mono',monospace;font-size:15px}
    .l{opacity:0;animation:show .01s forwards}
    .cur{fill:#FFD700;animation:blink 1s steps(1) infinite}
    @keyframes show{to{opacity:1}}
    @keyframes blink{50%{opacity:0}}
  </style>
  <rect x="1" y="1" width="618" height="268" rx="14" fill="#0D0D0D" stroke="#8B0000" stroke-width="2"/>
  <path d="M1 15a14 14 0 0 1 14-14h590a14 14 0 0 1 14 14v21H1z" fill="#1A0000"/>
  <circle cx="24" cy="18" r="6" fill="#8B0000"/>
  <circle cx="46" cy="18" r="6" fill="#FFD700"/>
  <circle cx="68" cy="18" r="6" fill="#FFFFFF"/>
  <text x="310" y="23" fill="#777777" text-anchor="middle" style="font-size:12px">antonio@mint: ~</text>

  <text class="l" x="26" y="78"  fill="#FFD700" style="animation-delay:.4s">antonio@mint:~$ <tspan fill="#FFFFFF">whoami</tspan></text>
  <text class="l" x="26" y="104" fill="#FFFFFF" style="animation-delay:1.1s">Antonio Vicente García Corrales</text>
  <text class="l" x="26" y="142" fill="#FFD700" style="animation-delay:1.9s">antonio@mint:~$ <tspan fill="#FFFFFF">cat about.txt</tspan></text>
  <text class="l" x="26" y="168" fill="#BBBBBB" style="animation-delay:2.6s">├─ carrera   : Ingeniería de Sistemas · 6to sem.</text>
  <text class="l" x="26" y="192" fill="#BBBBBB" style="animation-delay:3.1s">├─ enfoque   : ML · IA Generativa · Full Stack</text>
  <text class="l" x="26" y="216" fill="#BBBBBB" style="animation-delay:3.6s">├─ ubicación : Bolivia</text>
  <text class="l" x="26" y="240" fill="#BBBBBB" style="animation-delay:4.1s">╰─ instagram : @ant_nin_o<tspan class="cur"> █</tspan></text>
</svg>
"""
open("assets/whoami.svg", "w", encoding="utf-8").write(WHOAMI)


# ───────────────────────── RADARES ─────────────────────────
def radar(skills, out):
    size, c, r = 500, 250, 150
    n = len(skills)

    def pt(i, v):
        a = -math.pi / 2 + 2 * math.pi * i / n
        return c + r * v / 100 * math.cos(a), c + r * v / 100 * math.sin(a)

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        "<style>.poly{transform-origin:250px 250px;animation:grow 1.6s ease-out both}"
        ".pt{animation:pulse 2.4s ease-in-out infinite}"
        "@keyframes grow{from{transform:scale(0);opacity:0}to{transform:scale(1);opacity:1}}"
        "@keyframes pulse{50%{opacity:.35}}</style>",
        f'<rect x="1" y="1" width="{size-2}" height="{size-2}" rx="16" fill="{FONDO}" stroke="{ROJO}" stroke-width="2"/>',
    ]
    for lv in (25, 50, 75, 100):
        pts = " ".join("%.0f,%.0f" % pt(i, lv) for i in range(n))
        s.append(f'<polygon points="{pts}" fill="none" stroke="{GRID}"/>')
    for i, name in enumerate(skills):
        x, y = pt(i, 100)
        s.append(f'<line x1="{c}" y1="{c}" x2="{x:.0f}" y2="{y:.0f}" stroke="{GRID}"/>')
        lx, ly = pt(i, 125)
        s.append(
            f'<text x="{lx:.0f}" y="{ly:.0f}" fill="{TEXTO}" font-family="monospace" '
            f'font-size="14" text-anchor="middle" dominant-baseline="middle">{name}</text>'
        )
    pts = " ".join("%.0f,%.0f" % pt(i, v) for i, v in enumerate(skills.values()))
    s.append(
        f'<g class="poly"><polygon points="{pts}" fill="{ACENTO}" fill-opacity="0.3" '
        f'stroke="{ACENTO}" stroke-width="2"/>'
    )
    for i, v in enumerate(skills.values()):
        x, y = pt(i, v)
        s.append(f'<circle class="pt" cx="{x:.0f}" cy="{y:.0f}" r="4" fill="{ACENTO}" style="animation-delay:{i*0.3:.1f}s"/>')
    s.append("</g></svg>")
    open(out, "w", encoding="utf-8").write("\n".join(s))


# Cambia los números (0 a 100) por tu nivel real
radar({"ML / IA": 80, "Full Stack": 75, "Bases de datos": 70, "Backend": 75, "Linux": 70, "Automatización": 65},
      "assets/radar.svg")
radar({"Python": 85, "TypeScript": 70, "JavaScript": 70, "SQL": 70, "C#": 55, "C++": 50},
      "assets/radar-langs.svg")

# ───────────────────────── README ─────────────────────────
SI = "https://skillicons.dev/icons?i="
README = f"""<div align="center">

[![Antonio Vicente García Corrales](assets/banner.svg)](https://github.com/ANTONIO30-09)

[![Typing](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=22&duration=2600&pause=700&color=FFD700&center=true&vCenter=true&width=900&lines=Ingenier%C3%ADa+de+Sistemas+(6to+semestre);Machine+Learning+%7C+IA+Generativa+%7C+Full+Stack;Python+%7C+FastAPI+%7C+React+%7C+TypeScript+%7C+SQL;Remoto+%2F+H%C3%ADbrido+%7C+Pr%C3%A1cticas+%2F+Junior)](https://github.com/ANTONIO30-09)

![profile views](https://komarev.com/ghpvc/?username=ANTONIO30-09&style=flat&color=FFD700&label=profile+views)

[![Email](https://img.shields.io/badge/Email-antoniovicentegarciacorrales2%40gmail.com-000000?style=for-the-badge&logo=gmail&logoColor=white&labelColor=8B0000)](mailto:antoniovicentegarciacorrales2@gmail.com)
![Ubicación](https://img.shields.io/badge/Ubicaci%C3%B3n-Bolivia-000000?style=for-the-badge&logo=google-maps&logoColor=white&labelColor=8B0000)
![Teléfono](https://img.shields.io/badge/Tel%C3%A9fono-78%2035%2028%2079-000000?style=for-the-badge&logo=whatsapp&logoColor=white&labelColor=8B0000)

</div>

---

## `$ whoami`

<table>
  <tr>
    <td align="center" width="240">
      <img src="assets/foto.png" width="220" alt="Antonio" />
    </td>
    <td>
      <img src="assets/whoami.svg" width="620" alt="Terminal whoami de Antonio" />
    </td>
  </tr>
</table>

---

## `$ cat tech-stack.yaml`

| `antonio@mint:~$ cat tech-stack.yaml` | |
| :--- | :--- |
| `├─ ✦ lenguajes:` <br> <img src="{SI}py,ts,js,cs,cpp" alt="lenguajes" /> <br> `Python · TypeScript · JavaScript · C# · C++` | `├─ ◈ ml_ia:` <br> <img src="{SI}pytorch,tensorflow,numpy,pandas" alt="ml" /> <br> `PyTorch · TensorFlow · NumPy · Pandas` |
| `├─ ⚙ backend_frontend:` <br> <img src="{SI}fastapi,react,nodejs,html,css" alt="web" /> <br> `FastAPI · React · Node.js · HTML · CSS` | `├─ ▣ bases_de_datos:` <br> <img src="{SI}postgres,mysql" alt="db" /> <br> `PostgreSQL · MySQL · SQL` |
| `╰─ ⌁ herramientas:` <br> <img src="{SI}linux,bash,git,github,docker,vscode" alt="tools" /> <br> `Linux · Bash · Git · GitHub · Docker · VS Code` | `status: learning  ·  environment: always-on` |

---

## `$ ./skills --radar`

<div align="center">

<img src="assets/radar.svg" width="380" alt="Radar de habilidades" />
<img src="assets/radar-langs.svg" width="380" alt="Radar de lenguajes" />

`signals: skill_radar · language_radar · status: healthy`

</div>

---

## `$ connect --socials`

<div align="center">

[![Instagram](https://img.shields.io/badge/Instagram-ant__nin__o-000000?style=for-the-badge&logo=instagram&logoColor=white&labelColor=8B0000)](https://instagram.com/ant_nin_o)
[![GitHub](https://img.shields.io/badge/GitHub-ANTONIO30--09-000000?style=for-the-badge&logo=github&logoColor=white&labelColor=8B0000)](https://github.com/ANTONIO30-09)
[![Email](https://img.shields.io/badge/Gmail-Escr%C3%ADbeme-000000?style=for-the-badge&logo=gmail&logoColor=white&labelColor=8B0000)](mailto:antoniovicentegarciacorrales2@gmail.com)

Hecho con 💛 y mucho café desde Bolivia · @ANTONIO30-09

</div>
"""
open("README.md", "w", encoding="utf-8").write(README)
print("Listo: assets/banner.svg, whoami.svg, radar.svg, radar-langs.svg y README.md")
