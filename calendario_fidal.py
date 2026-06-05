from ics import Calendar, Event
from datetime import datetime
import os

calendar = Calendar()
conteggio_totale = 0

# ✅ DATI GARE
gare = [
    {"data": "12/06/2026", "titolo": "Meeting Ragazzi", "luogo": "Firenze", "categoria": "ragazzi", "regione": "toscana"},
    {"data": "15/06/2026", "titolo": "Campionati Cadetti", "luogo": "Prato", "categoria": "cadetti", "regione": "toscana"},
    {"data": "20/06/2026", "titolo": "Trofeo Giovanile", "luogo": "Pistoia", "categoria": "allievi", "regione": "toscana"},
    {"data": "22/06/2026", "titolo": "Meeting Master", "luogo": "Roma", "categoria": "master", "regione": "lazio"},
]

# ✅ FILTRI
CATEGORIE_OK = ["esordienti", "ragazzi", "cadetti", "allievi", "juniores"]

gare_filtrate = []

for g in gare:
    if g["regione"] != "toscana":
        continue
    
    if g["categoria"] not in CATEGORIE_OK:
        continue

    gare_filtrate.append(g)

print("Gare filtrate:", len(gare_filtrate))

# ✅ CREAZIONE EVENTI
for g in gare_filtrate:
    data_evento = datetime.strptime(g["data"], "%d/%m/%Y")

    evento = Event()
    evento.name = f"{g['titolo']} ({g['categoria']})"
    evento.begin = data_evento
    evento.make_all_day()
    evento.location = g["luogo"]

    calendar.events.add(evento)
    conteggio_totale += 1

# ✅ SALVATAGGIO
os.makedirs("docs", exist_ok=True)

with open("docs/calendario_toscana.ics", "w", encoding="utf-8") as f:
    f.writelines(calendar)

print(f"✅ Creato file docs/calendario_toscana.ics con {conteggio_totale} eventi")
