"""Agrega Contacto/Cobertura al respaldo del borrador sin reemplazar la portada.
No envía nada. Uso: uv run --with beautifulsoup4 --with tinycss2 python armar_contacto.py CARPETA
CARPETA contiene borrador-antes-contacto.json, leído del borrador ADICIO 2.
"""
import argparse
import copy
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
import tinycss2 as css
from bs4 import BeautifulSoup
import armar_home as a
from compilar_portada import ASSETS, decls, selectors, write_rule

p=argparse.ArgumentParser(); p.add_argument('carpeta',type=Path); args=p.parse_args(); out=args.carpeta
source=a.soup.select_one('#contacto')
assert source and source['data-ghl']=='section'
texts=copy.deepcopy(source)

def mark(node, kind, id_, cls=None, sample=None):
    node['id']=id_; node['data-ghl']=kind
    if cls: node['class']=list(node.get('class',[]))+cls.split()
    if sample:
        for table in (a.E19,a.E39): table[id_]=dict(table[sample])

for i, li in enumerate(source.select('.datos > li')):
    mark(li,'column',f'ad-contacto-{i}')
    img=li.img; mark(img,'image',f'ad-contacto-icono-{i}', 'dato-icono','a160')
    rotulo=li.select_one('.dato-rotulo'); rotulo.name='p'
    mark(rotulo,'paragraph',f'ad-contacto-rotulo-{i}', sample='a162')
    val=li.find(['a','span'],recursive=False)
    v=a.soup.new_tag('p'); val.wrap(v)
    mark(v,'paragraph',f'ad-contacto-valor-{i}', 'dato-valor','a162')
    if val.get('href','').startswith('tel:'):
        assert re.fullmatch(r'tel:\+\d{8,15}',val['href']), 'tel: inválido en fuente aprobada; no se reemplaza por supuesto'

cuerpo=source.select_one('.cobertura-cuerpo'); mark(cuerpo,'row','ad-cobertura-cuerpo')
caja=cuerpo.select_one('.mapa-caja'); mark(caja,'column','ad-cobertura-mapa')
zonas=cuerpo.select_one('.zonas'); zonas.wrap(a.soup.new_tag('div')); mark(zonas.parent,'column','ad-cobertura-lista')
section=a.build_section(source,2)
by={e['id']:e for e in section['elements']}
assert len(by)==len(section['elements']) and set(a.MAPA.values()) <= (set(by)|{section['id']})
for n in source.select('[data-ghl="headline"], [data-ghl="paragraph"], [data-ghl="image"], [data-ghl="button"]'):
    assert n['id'] in a.MAPA, n['id']
    e=by[a.MAPA[n['id']]]
    if n.name in ('h2','p'):
        text=BeautifulSoup(e['extra']['text']['value'],'html.parser')
        fold=lambda s:' '.join(s.split())
        assert fold(text.get_text())==fold(n.get_text()),n['id']
        assert [x.get('href') for x in text.select('a')]==[x.get('href') for x in n.select('a')]
    if n.name=='img':
        assert e['extra']['imageProperties']['value']['altText']==n.get('alt','')
# Conservar los links originales también en los botones.
for b in texts.select('.redes a'):
    assert by[a.MAPA[b['id']]]['extra']['visitWebsite']['value']['url']==b['href']

before=json.loads((out/'borrador-antes-contacto.json').read_text(encoding='utf8'))
pd=copy.deepcopy(before['pd'])
assert [s['id'] for s in pd['sections']]==['section-cabecera','section-inicio']
assert all(s['pageId']==a.PAGE and s['locationId']==a.LOC and s['funnelId']==a.FUNNEL for s in pd['sections']+[section])
assert not(set(by)&{e['id'] for s in pd['sections'] for e in s['elements']})
pd['sections'].append(section)

classes=set(c for n in [source,*source.select('[class]')] for c in n.get('class',[]))|{'fila','col','redes-bloque'}
layout={'display','grid-template-columns','grid-template-rows','gap','column-gap','row-gap','align-items','justify-content','flex-wrap'}
rows={'fila-contacto','datos','dato','redes','cobertura-cuerpo','zonas','zona'}

def rule(sel, ds):
    names=set(re.findall(r'\.([a-z][\w-]*)',sel))
    if sel==':root': return write_rule('.s-contacto',[(k,v) for k,v in ds if k.startswith('--')])
    if sel in ('h2','p','a',':focus-visible'):
        return write_rule('.s-contacto '+sel,[(k,v) for k,v in ds if k!='color'])
    if not names or not names<=classes: return ''
    if names=={'col'}: return ''
    sel=sel.replace('.datos li > span:last-child','.dato-valor p').replace('.datos li','.dato')
    sel=sel.replace('.tarjeta-contacto > p','.tarjeta-contacto p').replace('.tarjeta-cobertura > p','.tarjeta-cobertura p')
    sel=sel.replace('.zona p:last-child','.zona .c-paragraph:last-child p').replace('.dato-rotulo','.dato-rotulo p')
    sel=re.sub(r'\.zona-nombre(?=\s|$)', '.zona-nombre p',sel)
    if sel=='.red' or sel.startswith('.red:') or sel=='.red-wa': sel='a'+sel
    if sel=='.titulo-rotulo': sel+='.text-output h2'
    # No fijar el color de los textos por CSS cuando GHL ya lo guarda correctamente.
    ds=[(k,v) for k,v in ds if k!='color' or any(c in sel for c in ('.dato','.zona','.red'))]
    target=sel if sel=='.s-contacto' else '.s-contacto '+sel
    inn=any(sel.endswith('.'+c) for c in rows)
    if inn:
        child=' > .inner'
        if sel.endswith(('.dato','.zona')): child=' > .inner'
        return write_rule(target,[(k,v) for k,v in ds if k not in layout])+write_rule(target+child,[(k,v) for k,v in ds if k in layout])
    return write_rule(target,ds)

def convert(rules):
    parts=[]
    for r in rules:
        if r.type=='qualified-rule': parts.extend(rule(s,decls(r.content)) for s in selectors(r.prelude))
        elif r.type=='at-rule' and r.lower_at_keyword=='media' and r.content:
            inner=convert(css.parse_rule_list(r.content,skip_comments=True,skip_whitespace=True))
            if inner: parts.append('@media '+css.serialize(r.prelude).strip()+'{\n'+inner+'}\n')
    return ''.join(parts)

sty=convert(css.parse_stylesheet((a.W31/'estilos.css').read_text(encoding='utf8'),skip_comments=True,skip_whitespace=True))
bridge=(a.H/'contacto-puentes.css').read_text(encoding='utf8')
# Builder stores the existing test row without the synthetic class because it
# has no measured source rectangle. Scope its rules by its native map child.
sty=sty.replace('.cobertura-cuerpo', ':is(.cobertura-cuerpo,.c-row:has(> .inner > .mapa-caja))').replace(' h2.anim-titular{', ' .anim-titular h2{')
icons='\n'.join('.s-contacto .redes .c-column:nth-child(%d) a.red::before{background-image:url("%s%s")}'%(i,ASSETS,b.img['src'].split('/')[-1]) for i,b in enumerate(texts.select('.redes a'),1))
# El editor guarda su CSS de página, el head y el body actuales. Solo se amplía el CSS.
assert isinstance(pd['pageStyles'],str) and len(pd['pageStyles'])>1000 and 'ADICIO PILOTO' in pd['trackingCode']['footerCode']
assert 'ADICIO CONTACTO' not in pd['pageStyles']
contact_css='\n/* ADICIO CONTACTO */\n'+sty+'\n'+bridge+'\n'+icons
(out/'contacto.css').write_text(contact_css,encoding='utf8')
pd['pageStyles']+=contact_css
# La capa original encuentra las zonas por atributo. Se registra antes del script actual y
# espera la hidratación si el HTML todavía no está listo. No toca los textos editables.
pre="""<script>(()=>{function zonas(){document.querySelectorAll('.s-contacto .zona-caba,.s-contacto .zona-norte,.s-contacto .zona-costa').forEach(n=>{const z=['caba','norte','costa'].find(k=>n.classList.contains('zona-'+k));if(z)n.dataset.zona=z})}zonas();document.addEventListener('DOMContentLoaded',zonas,{once:true});document.addEventListener('hydrationDone',zonas);window.addEventListener('hydrationDone',zonas)})();</script>"""
pd['trackingCode']['footerCode']=pre+'\n'+pd['trackingCode']['footerCode']
assert pd['sections'][:2]==before['pd']['sections']
(out/'borrador-contacto.json').write_text(json.dumps(pd,ensure_ascii=False),encoding='utf8')
(out/'mapa-contacto.json').write_text(json.dumps(a.MAPA,ensure_ascii=False,indent=2),encoding='utf8')
print(section['id'],len(by),'elementos',len(contact_css.encode()),'bytes de CSS; portada intacta en datos')
