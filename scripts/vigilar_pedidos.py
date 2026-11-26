"""Wait until someone other than Hermes/Nacho requests the short Vercel alias (e.g. GHL's Start from URL checker).

Needs templates/vercel-middleware-log.js deployed as middleware.js. Exits with one line per outside request
(after a 20 s pause to gather the burst), or with a 'no requests' line at the time cap.
Run with terminal(background=true, notify=true) so the chat wakes up when it exits.

Uso: python vigilar_pedidos.py --alias adicio-ghl-prueba.vercel.app --dir <deploy folder> [--minutos 25] [--ignorar-ip 181.99.64.131]
"""
import argparse, json, re, subprocess, sys, time

ap = argparse.ArgumentParser()
ap.add_argument('--alias', required=True, help='short alias only, e.g. <project>.vercel.app')
ap.add_argument('--dir', required=True, help='deploy folder (linked to the Vercel project)')
ap.add_argument('--minutos', type=float, default=25)
ap.add_argument('--ignorar-ip', action='append', default=[], help='own public IPs (repeatable)')
a = ap.parse_args()

MIOS = ('prueba-hermes', 'curl/', 'python-requests', 'python-urllib', 'node-fetch', 'axios')
inicio = time.time(); vistos = set(); hallados = []
while time.time() - inicio < a.minutos * 60:
    try:
        out = subprocess.run(f'vercel logs {a.alias} --since 30m --json', shell=True, cwd=a.dir,
                             capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90).stdout
    except Exception:
        out = ''
    for linea in out.splitlines():
        try:
            d = json.loads(linea)
        except Exception:
            continue
        # Hash aliases get Vercel's own screenshot bot after each deploy: watch only the alias handed to GHL.
        if d.get('domain') != a.alias:
            continue
        m = re.search(r'\{.*\}', d.get('message') or '')
        if not m:
            continue
        try:
            r = json.loads(m.group(0))
        except Exception:
            continue
        ua = r.get('ua') or ''
        ip = r.get('ip') or ''
        clave = (d.get('timestamp'), r.get('url'), ua)
        if clave in vistos or any(x in ua for x in MIOS) or any(ip.startswith(x) for x in a.ignorar_ip):
            continue
        vistos.add(clave); hallados.append(r)
    if hallados:
        time.sleep(20)
        print(f'{len(hallados)} pedido(s) de afuera a {a.alias}:')
        for r in hallados[:40]:
            print(json.dumps(r, ensure_ascii=False))
        sys.exit(0)
    time.sleep(15)
print(f'Sin pedidos de afuera a {a.alias} en {a.minutos:.0f} min: el verificador no llegó a la página.')
