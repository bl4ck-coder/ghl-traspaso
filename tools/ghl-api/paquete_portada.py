"""Entrega CSS y Body de seguimiento del piloto; no escribe en GHL."""
import argparse
from pathlib import Path
from compilar_portada import H, S, build

p=argparse.ArgumentParser();p.add_argument('salida',type=Path); a=p.parse_args()
a.salida.mkdir(parents=True, exist_ok=True)
css=build()
menu=(H/'portada-menu.js').read_text(encoding='utf-8')
source=(S/'capa/capa.js').read_text(encoding='utf-8')
# Reusar el original; sólo montar en la página que tiene esta portada.
js=menu+"\nif (document.getElementById('section-inicio') && document.getElementById('section-cabecera')) {\n"+source+'\n}\n'
motion=(S/'capa/capa.css').read_text(encoding='utf-8')
assert '</script' not in js.lower() and '</style' not in motion.lower()
for name,value in {'portada.css':css, 'portada.js':js, 'body-portada.html':'<!-- ADICIO PILOTO v1 -->\n<style>'+motion+'</style>\n<script>'+js+'</script>'}.items():
    (a.salida/name).write_text(value,encoding='utf-8')
    print(name,len(value.encode()))
