# ghl-traspaso

Skill + herramientas para pasar páginas hechas con IA/código a GoHighLevel (GHL / BizurAI) usando sus elementos nativos.

## Qué hay
- `SKILL.md`, `references/`, `scripts/`, `templates/`: la skill `gohighlevel-pages` (rutas de traspaso, hechos del builder, reglas SEO y reglas del equipo de la reunión del 25/11).
- `tools/ghl-api/`: scripts del pipeline (abrir el Chromium con sesión, armar la página, subir borradores, verificar).
- `tools/inventario/`: lectores de solo lectura para inventariar una subcuenta.
- [Caso ADICIO · Ronda 4](references/adicio-fiel-ronda-4.md): resultados por borrador, causas comprobadas, arreglos probados en páginas de prueba y pendientes de preview, animaciones y editor.

## Cómo se usa
1. Leé `SKILL.md` (el agente la carga sola si está en su carpeta de skills).
2. Abrí Chromium con `--remote-debugging-port=9333`, logueate vos en GHL y usá los scripts de `tools/` contra esa pestaña.
3. Los ids (`LOCATION_ID`, `PAGE_ID`, `FORM_ID`, `FUNNEL_ID`) son placeholders: poné los de tu subcuenta. Los scripts de `tools/` tienen rutas relativas de ejemplo (`../ghl-api`); ajustalas.
4. Nunca se publica solo: los scripts guardan borradores.

## ADVERTENCIA
`tools/` usa la **API interna de GHL** (token de la sesión del navegador), no la API oficial. Eso **va contra los términos de servicio de GHL**. Uso bajo tu propia responsabilidad. No se incluye ningún token, cookie ni sesión; no los subas.
