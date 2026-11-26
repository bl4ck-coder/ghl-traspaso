"""Compila reglas originales de la portada para el HTML nativo de GHL. No accede al editor."""
from pathlib import Path
import argparse
import re
import tinycss2 as css

H = Path(__file__).resolve().parent
S = H.parents[1] / '31-adicio-home-ghl/sitio'
ASSETS = 'https://adicio-ghl-prueba.vercel.app/media/'
SCOPE = ':is(.s-nav,.s-hero)'
CLASSES = set('s-nav fila fila-nav col-logo logo logo-img col-menu menu menu-boton menu-rayas menu-casilla col-accion s-hero fila-hero col-hero-texto bajada firma firma-foto firma-texto botones col-hero-foto hero-foto fila-pilares pilar pilar-texto boton boton-primario boton-secundario boton-wa vidrio hero-zonas enlace-firma'.split())
LAYOUT = {'display', 'gap', 'row-gap', 'column-gap', 'grid-template-columns', 'align-items', 'justify-content', 'flex-wrap', 'flex-direction'}
ROWS = {'.fila-nav', '.fila-hero', '.fila-pilares', '.botones', '.firma', '.pilar'}
TEXT = {'bajada', 'firma-texto', 'pilar-texto', 'hero-zonas'}


def decls(tokens):
    return [(d.lower_name, css.serialize(d.value).strip()) for d in css.parse_declaration_list(tokens, skip_comments=True, skip_whitespace=True) if d.type == 'declaration']


def selectors(toks):
    out, cur = [], []
    for t in toks:
        if t.type == 'literal' and t.value == ',':
            out.append(css.serialize(cur).strip()); cur = []
        else:
            cur.append(t)
    return out + [css.serialize(cur).strip()]


def write_rule(s, ds):
    if not ds:
        return ''
    return s + '{' + ';'.join(k+':'+re.sub(r'(?<=\")media/', ASSETS, v)+' !important' for k,v in ds) + '}\n'


def transform(sel, d):
    if sel == ':root':
        return write_rule(SCOPE, [(k,v) for k,v in d if k.startswith('--')])
    if sel == 'body':
        return write_rule(SCOPE, [(k,v) for k,v in d if k in ('font-family','font-size','line-height')])
    if sel in ('a','h1','h2','h3','p',':focus-visible'):
        s = SCOPE + ' ' + sel
    else:
        names = set(re.findall(r'\.([a-z][\w-]*)', sel))
        if not names or not names <= CLASSES:
            return ''
        if any(x in sel for x in ('menu-casilla','menu-boton','menu-rayas')) or sel.startswith('.menu'):
            return ''  # markup propio del menú: el adaptador conserva el de GHL
        sel = re.sub(r'(?<= )\.enlace-firma\b', 'a', sel)
        if sel == '.enlace-firma':
            sel = '.firma-texto a'
        for c in TEXT:
            if sel.endswith('.'+c):
                sel += ' p'; break
        s = sel if sel.startswith(('.s-nav','.s-hero')) else SCOPE + ' ' + sel
        if sel == '.col-menu':
            return ''
        ending = re.search(r'(\.[a-z][\w-]*)$', sel)
        if ending and ending.group() in ROWS:
            ld = [(k,v) for k,v in d if k in LAYOUT]
            return write_rule(s, [(k,v) for k,v in d if k not in LAYOUT]) + write_rule(s+' > .inner',ld)
    # Colores de texto y estados base quedan bajo los controles de GHL.
    d = [(k,v) for k,v in d if k != 'color' and not (k == 'background' and sel in ('.boton-primario','.boton-secundario','.boton-wa'))]
    return write_rule(s,d)


def convert(rules):
    result = []
    for r in rules:
        if r.type == 'qualified-rule':
            for s in selectors(r.prelude):
                result.append(transform(s,decls(r.content)))
        elif r.type == 'at-rule' and r.lower_at_keyword == 'media' and r.content:
            inner = convert(css.parse_rule_list(r.content, skip_whitespace=True, skip_comments=True))
            if inner:
                result.append('@media '+css.serialize(r.prelude).strip()+'{\n'+inner+'}\n')
    return ''.join(result)


def build():
    original = (S/'estilos.css').read_text(encoding='utf-8')
    adapt = (H/'portada-puentes.css').read_text(encoding='utf-8')
    return '/* ADICIO: reglas originales portadas; generado por compilar_portada.py */\n' + (H/'portada-reset.css').read_text(encoding='utf-8') + '\n' + convert(css.parse_stylesheet(original,skip_whitespace=True,skip_comments=True)) + adapt


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('salida', type=Path); a = p.parse_args()
    out = build(); a.salida.write_text(out, encoding='utf-8'); print(a.salida, len(out.encode()))
