"""Arma editor-paridad.css: copia de las reglas que solo valen en la página publicada,
reescritas para el DOM del editor de GHL. No cambia nada de lo publicado.

Diferencias del editor medidas el 24/11 (ADICIO 2):
- las columnas llevan `container-type: inline-size` -> si su ancho es `auto` miden 0 y el texto cae de a una letra;
- el texto no tiene `.text-output` (solo `.cheading-<id>` / `.cparagraph-<id>`) y suma un `div.tiptap`;
- los botones son `<button>`, no `<a>`.
Uso: uv run -q --with tinycss2 python armar_editor_paridad.py <carpeta con los .css cargados>
"""
import re, sys
from pathlib import Path
import tinycss2 as css

ARCHIVOS = ['portada.css', 'contacto.css', 'resto.css', 'resto-ajuste.css', 'ajuste-redes.css',
            'pie-enlaces.css', 'pulido-1.css', 'pulido-2.css']
TXT = ':is([class*="cheading-"],[class*="cparagraph-"])'


def reescribir(sel):
    s = sel
    s = re.sub(r'\.text-output\s*>\s*div', TXT + ' div', s)
    s = s.replace('.text-output', TXT)
    s = re.sub(r'\ba(\.(?:red|red-wa|red-circulo|boton)\b)', r'button\1', s)
    return s


def recorrer(reglas, salida, envoltura=None):
    for r in reglas:
        if r.type == 'qualified-rule':
            sel = css.serialize(r.prelude).strip()
            nuevo = reescribir(sel)
            if nuevo != sel:
                bloque = f'{nuevo}{{{css.serialize(r.content)}}}'
                salida.append(f'{envoltura}{{{bloque}}}' if envoltura else bloque)
        elif r.type == 'at-rule' and r.lower_at_keyword in ('media', 'supports') and r.content:
            cond = f'@{r.lower_at_keyword} {css.serialize(r.prelude).strip()}'
            hijas = css.parse_rule_list(r.content, skip_comments=True, skip_whitespace=True)
            recorrer(hijas, salida, cond if not envoltura else envoltura)


def main():
    d = Path(sys.argv[1])
    out = ['/* ADICIO EDITOR PARIDAD 1 · solo afecta al editor; lo publicado no tiene estos nodos */',
           '@scope (#page-creator .previewer) {',
           '.page-wrapper > .c-section :is(.c-column,.c-nested-column){container-type:normal!important}',
           '.s-contacto .redes button.red:after{content:none!important}',
           '.s-pie .redes-pie button.red-circulo .main-heading-group{position:static!important}']
    n = 0
    for f in ARCHIVOS:
        p = d / f
        if not p.exists():
            continue
        reglas = css.parse_stylesheet(p.read_text(encoding='utf-8'), skip_comments=True, skip_whitespace=True)
        antes = len(out)
        recorrer(reglas, out)
        n += len(out) - antes
        print(f, len(out) - antes)
    out.append('}')
    (d / 'editor-paridad.css').write_text('\n'.join(out) + '\n', encoding='utf-8')
    print('reglas reescritas', n, 'bytes', len('\n'.join(out)))


if __name__ == '__main__':
    main()
