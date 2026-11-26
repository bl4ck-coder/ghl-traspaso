"""Prueba reversible del título nativo. Solo actúa sobre ADICIO 2, nunca publica."""
import json, re, time, urllib.request
from html.parser import HTMLParser
from editor9333 import Editor

PAGE='PAGE_ID'
PATH='/location/LOCATION_ID/page-builder/'+PAGE
URL='https://sites.leadconnectorhq.com/preview/'+PAGE
ORIGINAL='Cuidado de personas mayores en casa, con respaldo de enfermería'
TEST=ORIGINAL+' · Prueba temporal'
e=Editor()
def j(s):
    return e.js('(()=>{if(location.pathname!=='+json.dumps(PATH)+'||!document.body.innerText.includes("ADICIO 2"))throw Error("Destino inesperado");'+s+'})()')
SEL='.s-hero .tiptap h1'
def editor_value():
    return j('return document.querySelector('+json.dumps(SEL)+')?.textContent;')

def set_title(text):
    coords=j('const h=document.querySelector('+json.dumps(SEL)+');h.scrollIntoView({block:"center"});const r=h.getBoundingClientRect();return [r.x+28,r.y+24];')
    for t in ('mousePressed','mouseReleased'):
        e.cmd('Input.dispatchMouseEvent',type=t,x=coords[0],y=coords[1],button='left',clickCount=1)
    assert j('const h=document.querySelector('+json.dumps(SEL)+');const p=h.closest(".tiptap");if(!p.isContentEditable)return false;p.focus();const r=document.createRange();r.selectNodeContents(h);const s=getSelection();s.removeAllRanges();s.addRange(r);return s.toString()===h.textContent;'), 'Título no seleccionado en el editor'
    e.cmd('Input.insertText',text=text)
    assert editor_value()==text, 'No se editó el titular nativo'
    assert j('document.activeElement.blur(); const b=document.querySelector("#pg-website-builder__btn--save");if(!b||b.disabled)return false;b.click();return true;')

class Title(HTMLParser):
    def __init__(self): super().__init__(); self.on=False;self.text=[]
    def handle_starttag(self,t,a):
        if t=='h1': self.on=True
    def handle_endtag(self,t):
        if t=='h1': self.on=False
    def handle_data(self,s):
        if self.on:self.text.append(s)

def preview(expected):
    deadline=time.monotonic()+35
    while time.monotonic()<deadline:
        r=urllib.request.Request(URL+'?pilot-check='+str(time.time_ns()),headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(r,timeout=10) as f: html=f.read().decode('utf-8')
        p=Title(); p.feed(html)
        if ''.join(p.text).strip()==expected:
            assert 'anim-titular' in html and 'ADICIO PILOTO' in html
            return
        time.sleep(2)
    raise AssertionError('La vista previa no refleja el H1 esperado: '+repr(''.join(p.text)))

assert editor_value()==ORIGINAL
try:
    set_title(TEST);preview(TEST)
    print('Edición nativa y guardado: la vista previa muestra el texto temporal; conserva clase y capa.')
finally:
    current=editor_value()
    if current==TEST:
        set_title(ORIGINAL);preview(ORIGINAL)
        print('Restauración: vista previa vuelve a mostrar el H1 original.')
    elif current!=ORIGINAL:
        raise AssertionError('Valor inesperado durante restauración; no se sobreescribe: '+repr(current))
