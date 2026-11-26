"""Compila las 7 secciones que faltaban; no escribe en GHL. Parte de antes-lote.json.
Uso: uv run -q --with beautifulsoup4 --with tinycss2 python armar_resto.py CARPETA
"""
import argparse, copy, json, re
from pathlib import Path
from urllib.parse import urlparse
import tinycss2 as css
from bs4 import BeautifulSoup
import armar_home as a
from compilar_portada import decls, selectors, write_rule

p=argparse.ArgumentParser();p.add_argument('out',type=Path);args=p.parse_args();d=args.out
src=BeautifulSoup((a.W31/'importar.html').read_text(encoding='utf8'),'html.parser')
order=['a001','inicio','servicios','quienes','como','novedades','contacto','preguntas','blog','a192']
keep={'a001':'section-cabecera','inicio':'section-inicio','contacto':'section-contacto'}
blocks=[src.find(id=k) for k in order if k not in keep]
assert all(blocks)
original=copy.deepcopy(blocks)

def mark(n, typ, id=None, cls=None):
 assert n is not None,(typ,id,cls)
 n['data-ghl']=typ
 if id:n['id']=id
 if cls:n['class']=list(n.get('class',[]))+cls.split()
 return n

def visual(n, keys):
 for t in (a.E19,a.E39):
  for k in keys:
   assert k in t
  t[n['id']]=dict(t[keys[0]])

serv=src.select_one('.servicios');mark(serv,'row','ad-servicios-pila');visual(serv,['a073'])
for i,card in enumerate(serv.select('.servicio'),1):
 foto=card.select_one('.servicio-foto');txt=card.select_one('.servicio-texto')
 # Column inside column becomes a nested row with the native column intact.
 mark(foto,'column',f'ad-servicio-foto-{i}');mark(txt,'column',f'ad-servicio-texto-{i}')
 both=src.new_tag('div');mark(both,'row',f'ad-servicio-par-{i}','servicio-par');visual(both,[card['id']]);card.insert(0,both);both.append(foto.extract());both.append(txt.extract())
retr=mark(src.select_one('.equipo-retrato'),'column','ad-equipo-retrato')
quote=src.select_one('.cita'); classes=' '.join(quote['class']);mark(quote.p,'paragraph',cls=classes)
for i,n in enumerate(src.select('.tabla-como tr')):
 mark(n,'row',n.get('id') or 'ad-pasos-rubros','paso-rubros' if i==0 else None)
 if i==0: visual(n,['a120'])
 for j,c in enumerate(n.find_all(['th','td'],recursive=False),1):
  mark(c,'paragraph',cls='paso-titulo' if j==1 else 'paso-texto')
  if c.img:n.append(c.img.extract())
mark(src.select_one('.tabla-como'),'column','ad-tabla-como')
for h in src.select('.s-pie [data-ghl="list"]'):h['class']=list(h.get('class',[]))+['pie-lista']
for link in src.select('.s-pie li a[href^="#"]'):
 k=link['href'][1:]; link['href']='#'+(keep.get(k) or ('col-cobertura' if k=='cobertura' else 'section-'+k))
# Do not inherit any live form ID/action from the template or send a test lead.
form=src.select_one('.suscripcion')
for i,n in enumerate(src.select('.col-faq-intro > [data-ghl]')):n['class']=list(n.get('class',[]))+['faq-intro-'+str(i)]

before=json.loads((d/'antes-lote.json').read_text(encoding='utf8'))['pd']; pd=copy.deepcopy(before)
by_sec={s['id']:s for s in pd['sections']}; assert set(by_sec)==set(keep.values())
for s in pd['sections']:
 assert (s['pageId'],s['locationId'],s['funnelId'])==(a.PAGE,a.LOC,a.FUNNEL)
made={n['id']:a.build_section(n,order.index(n['id'])) for n in blocks}
allnodes={e['id']:e for s in made.values() for e in s['elements']}
assert len(allnodes)==sum(len(s['elements']) for s in made.values())
# a073 supplies dimensions only. Its page Y is not the position of this synthetic row.
allnodes[a.MAPA['ad-servicios-pila']]['wrapper']['marginTop']=a.V(0,'px')

def norm(v):return ' '.join(v.split())
def plain(v):return norm(BeautifulSoup(v,'html.parser').get_text())
for n in blocks:
 for v in n.select('[data-ghl="headline"],[data-ghl="paragraph"],[data-ghl="image"],[data-ghl="button"],[data-ghl="form"],[data-ghl="faq"]'):
  if v.find_parent(attrs={'data-ghl':'form'}) or (v.find_parent(attrs={'data-ghl':'faq'}) and v.find_parent('details')):continue
  q=allnodes[a.MAPA[v['id']]]; x=q['extra']
  kind=v['data-ghl']
  if kind in ('headline','paragraph'):assert plain(x['text']['value'])==norm(v.get_text()),v['id']
  if kind=='image':assert x['imageProperties']['value']['altText']==v.get('alt',''),v['id']
  if kind=='button':assert x['visitWebsite']['value']['url']==v['href'],v['id']
  if kind=='faq':
   pairs=[(norm(z.h3.get_text()),norm(z.p.get_text())) for z in v.select('details')]
   assert pairs==[(plain(z['heading']),plain(z['text'])) for z in x['faqList']['value']]
   for item in x['faqList']['value']:item['active']=False
  if kind=='form':
   x['formId']=a.V(''); x['action']=a.V('');x['visitWebsite']=a.V({'url':'','newTab':False})
   assert v is form

for e,k in a.ANCLAS:e['extra']['scrollToElement']=a.V(a.MAPA.get(k,keep.get(k,'section-'+k)))
# Change only section sequence on the already verified blocks.
pd['sections']=[by_sec[keep[k]] if k in keep else made[k] for k in order]
for i,s in enumerate(pd['sections']):s['sequence']=i
for k,v in by_sec.items():assert v['id']==k
for k in keep.values():
 b=next(s for s in before['sections'] if s['id']==k);assert by_sec[k]['elements']==b['elements']
assert pd['trackingCode']==before['trackingCode'] and pd['pageStyles']==before['pageStyles']

sections={n['class'][0] for n in blocks}
SCOPE=':is('+','.join('.'+s for s in sorted(sections))+')'
classes=set(c for n in blocks for t in [n,*n.select('[class]')] for c in t.get('class',[]))|{'fila','col','vidrio','vidrio-oscuro','cifra-signo','capa-apilando','capa-encendido','boton-texto','pregunta','respuesta','s-pie','solo-lector','js','main-heading-button'}
classes.update('titulo-chico suscripcion-email'.split())
layout=set('display grid-template-columns grid-template-rows gap column-gap row-gap align-items justify-items align-content justify-content flex-direction flex-wrap'.split())
rowclasses={'fila-intro','servicios','servicio-par','fila-cierre-servicios','fila-equipo','puntos','fila-cifras','fila-como','sello','paso','paso-rubros','fila-novedades','fila-faq','fila-blog','fila-pie','fila-pie-cierre','fila-pie-legal','redes-pie','col-faq-intro','cifra'}
textclasses={'bajada','rotulo','rotulo-claro','titulo-chico','sello-texto','numero','cifra-numero','cifra-rotulo','pie-modelo','pie-titulo','pie-lema','pie-legal'}


def project(sel,ds):
 names=set(re.findall(r'\.([a-z][\w-]*)',sel))
 if sel==':root':return write_rule(SCOPE,[(k,v) for k,v in ds if k.startswith('--')])
 if sel=='body':return write_rule(SCOPE,[(k,v) for k,v in ds if k in ('font','font-family','font-size','line-height')])
 if sel in ('h2','h3','p','a',':focus-visible','img','ul'):
  return write_rule(SCOPE+' '+sel,[(k,v) for k,v in ds if k not in ('color',)])
 if not names or not names<=classes:return ''
 if 'pregunta' in names or 'respuesta' in names:return '' # Native FAQ has different markup; bridge measured after save.
 orig=sel
 sel=sel.replace('.boton-texto','.main-heading-button')
 sel=sel.replace('.tabla-como thead tr','.tabla-como .paso-rubros').replace('.tabla-como thead th','.tabla-como .paso-rubros p').replace('.tabla-como tbody th','.tabla-como .paso-titulo p').replace('.tabla-como tr.paso','.tabla-como .paso').replace('.tabla-como td','.tabla-como .paso-texto p').replace('.tabla-como th','.tabla-como .paso-titulo p')
 sel=sel.replace('.col-pie-lista ul.redes-pie','.col-pie-lista .redes-pie')
 # Text classes live on the editor wrapper, sizing targets the editable text inside.
 if re.fullmatch(r'(?:.+ )?\.[\w-]+',sel) and sel.rsplit('.',1)[-1] in textclasses:
  wrap=[(k,v) for k,v in ds if k.startswith(('margin','padding','border')) or k=='min-height']
  ink=[(k,v) for k,v in ds if (k,v) not in wrap and k!='color']
  return write_rule(SCOPE+' '+sel,wrap)+write_rule(SCOPE+' '+sel+' :is(h2,h3,p)',ink)
 s=sel if sel.startswith(tuple('.'+x for x in sections)) else SCOPE+' '+sel
 last=re.search(r'\.([\w-]+)$',sel)
 if last and last[1] in rowclasses and any(k in layout for k,v in ds):
  parts=write_rule(s,[(k,v) for k,v in ds if k not in layout]);ld=[(k,v) for k,v in ds if k in layout]
  if last[1]=='servicios':ld=[(k,v) for k,v in ld if k!='display']+[('display','block')]
  return parts+write_rule(s+' > .inner',ld)
 if sel in ('.servicio','.servicio-apoyo','.servicio-principal'):
  return write_rule(s,[(k,v) for k,v in ds if k not in layout])+write_rule(s+' .servicio-par > .inner',[(k,v) for k,v in ds if k in layout])
 return write_rule(s,ds)


def convert(rules):
 result=[]
 for r in rules:
  if r.type=='qualified-rule':result.extend(project(s,decls(r.content)) for s in selectors(r.prelude))
  elif r.type=='at-rule' and r.lower_at_keyword=='media' and r.content:
   xs=convert(css.parse_rule_list(r.content,skip_comments=True,skip_whitespace=True))
   if xs:result.append('@media '+css.serialize(r.prelude).strip()+'{\n'+xs+'}\n')
 return ''.join(result)

b=(a.H/'resto-puentes.css').read_text(encoding='utf8').replace('@scope@',SCOPE)
compiled='/* ADICIO LOTE RESTANTE */\n'+convert(css.parse_stylesheet((a.W31/'estilos.css').read_text(encoding='utf8'),skip_comments=True,skip_whitespace=True))+'\n'+b
icons=[]
for n in blocks:
 for btn in n.select('a[data-ghl="button"]:has(img)'):
  g=allnodes[a.MAPA[btn['id']]]; label='ad-icono-'+btn['id']; g['extra']['customClass']['value'].append(label)
  u=a.MEDIA+btn.img['src'].split('/')[-1]; assert urlparse(u).hostname=='adicio-ghl-prueba.vercel.app'
  icons.append(f'.{label}::after{{background-image:url("{u}")!important}}')
compiled+='\n'.join(icons)
compiled+='\n'+(a.H/'resto-ajuste.css').read_text(encoding='utf8')
assert len(list(css.parse_stylesheet(compiled,skip_comments=True,skip_whitespace=True)))>100
for name,value in [('lote.json',json.dumps(pd,ensure_ascii=False)),('resto.css',compiled),('mapa-lote.json',json.dumps(a.MAPA,ensure_ascii=False,indent=2))]:(d/name).write_text(value,encoding='utf8')
print('Orden:',[s['id'] for s in pd['sections']]);print('Nuevas:',[(s['id'],len(s['elements'])) for s in made.values()]);print('Nuevos elementos:',len(allnodes),'CSS:',len(compiled.encode()),'bytes. Los elementos previos y el Body se conservan.')
