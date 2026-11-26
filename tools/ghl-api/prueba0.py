"""Prueba 0: una sección nativa (H1 + párrafo de la home nueva) para comprobar que la escritura llega a «ADICIO pruba»."""
import json, funnel_page_builder as B
B.LOC, B.FUNNEL = "LOCATION_ID", "FUNNEL_ID"
h = B.heading("<h1>Cuidado de personas mayores en casa, con respaldo de enfermería</h1>", "#ffffff", 54, 34, 700, "Inter", align="left", tag="h1")
p = B.paragraph("<p>Hay personas que necesitan ayuda todos los días. Otras siguen siendo independientes y quieren contar con un seguimiento profesional.</p>", "#ffffff", 20, 17, 400, "Inter", align="left")
c = B.col([h, p], pad=(40, 40, 40, 40), width=100)
sec = B.section([B.row([c])], 1, bgcolor="#00639B", pad=(120, 0, 120, 0), mobilepad=(70, 0, 70, 0))
pd = B.build_page([sec])
for s in pd["sections"]:
    s.update({"pageId": "PAGE_ID", "funnelId": B.FUNNEL, "locationId": B.LOC})
json.dump(pd, open("../datos/prueba0-pagedata.json", "w", encoding="utf-8"), ensure_ascii=False)
print("secciones", len(pd["sections"]), "elementos", sum(len(s["elements"]) for s in pd["sections"]), "bytes", len(json.dumps(pd)))
