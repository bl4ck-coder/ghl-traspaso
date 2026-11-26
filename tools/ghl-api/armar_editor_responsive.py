"""Adapta los breakpoints de ADICIO al ancho del lienzo de GHL en el editor."""
import argparse,re
from pathlib import Path
import tinycss2 as css
from armar_editor_paridad import ARCHIVOS, reescribir
p=argparse.ArgumentParser();p.add_argument('carpeta',type=Path);a=p.parse_args()
width=re.compile(r'\(\s*(?:(?:min|max)-)?width\s*:[^()]+\)')
vw=re.compile(r'(?<=\d)(?:d|s|l)?vw\b')

def render(rules):
 out=[]
 for r in rules:
  if r.type=='qualified-rule':
   sel=css.serialize(r.prelude).strip();v=vw.sub('cqw',css.serialize(r.content));new=reescribir(sel)
   out.append(f'{sel}{{{v}}}')
   if new!=sel:out.append(f'{new}{{{v}}}')
  elif r.type=='at-rule' and r.lower_at_keyword in ('media','supports') and r.content:
   cond=css.serialize(r.prelude).strip(); mapped=[]
   if r.lower_at_keyword=='media':
    for alt in cond.split(','):
     cs=width.findall(alt)
     if cs:
      remain=re.sub(r'^\s*and\s+|\s+and\s*$', '',width.sub('',alt).strip()).strip()
      remain=re.sub(r'^and\s*|\s*and$', '',remain).strip()
      mapped.append((f'@container adicio-editor {" and ".join(cs)}',f'@media {remain}' if remain else None))
     else:mapped.append((f'@media {alt.strip()}',None))
   else:mapped=[(f'@supports {cond}',None)]
   inner='\n'.join(render(css.parse_rule_list(r.content,skip_whitespace=True,skip_comments=True)))
   for cond,ext in mapped:
    chunk=f'{cond}{{\n{inner}\n}}';out.append(f'{ext}{{\n{chunk}\n}}' if ext else chunk)
 return out

def responsive(rules):
 for r in rules:
  if r.type=='qualified-rule' and vw.search(css.serialize(r.content)):
   decl=[d for d in css.parse_declaration_list(r.content,skip_comments=True,skip_whitespace=True) if d.type=='declaration' and vw.search(css.serialize(d.value))]
   sel=css.serialize(r.prelude).strip();new=reescribir(sel);val=';'.join(d.name+':'+vw.sub('cqw',css.serialize(d.value))+('!important' if d.important else '') for d in decl)
   if val:yield f'{sel}{{{val}}}'+(f'\n{new}{{{val}}}' if new!=sel else '')
  elif r.type=='at-rule' and r.lower_at_keyword=='media' and r.content and width.search(css.serialize(r.prelude)):
   yield from render([r])

out=['/* ADICIO EDITOR LIENZO 1 */','#page-creator .previewer {container:adicio-editor / inline-size}', '@scope (#page-creator .previewer) {']
for f in ARCHIVOS:
 p=a.carpeta/f
 if not p.exists():continue
 out.extend(responsive(css.parse_stylesheet(p.read_text(encoding='utf8'),skip_comments=True,skip_whitespace=True)))
out += ['@container adicio-editor (max-width:420px){.s-contacto .redes>.inner{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}.s-contacto .redes>.inner>.c-column{width:100%!important;min-width:0!important}.s-contacto .redes button.red{font-size:16px!important;padding-inline:8px!important;gap:6px!important;max-width:100%}.s-contacto .redes button.red::before{width:22px;height:22px}}','}']
(a.carpeta/'editor-lienzo.css').write_text('\n'.join(out)+'\n',encoding='utf8')
print('Bloques:',len(out),'caracteres:',sum(map(len,out)))
