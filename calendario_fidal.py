from pypdf import PdfReader
from ics import Calendar, Event
from datetime import datetime
import os
import re

calendar = Calendar()
conteggio = 0

# ✅ leggi PDF
reader = PdfReader("BOZZA calendario estivo Toscana 2026.pdf")

testo = ""
for pagina in reader.pages:
    testo += pagina.extract_text() + "\n"

righe = testo.split("\n")

CATEGORIE_OK = ["ragazzi", "cadetti", "allievi", "juniores", "esordienti"]

mesi = {
    "gen": "01","feb": "02","mar": "03","apr": "04","mag": "05","giu": "06",
    "lug": "07","ago": "08","set": "09","ott": "10","nov": "11","dic": "12"
}

for riga in righe:
    
    riga_lower = riga.lower()

    # ✅ filtro giovanili
    if not any(cat in riga_lower for cat in CATEGORIE_OK):
        continue

    # ✅ trova data tipo 12-apr-26
    parti = riga.split()
    data_trovata = None

    for p in parti:
        if "-" in p and "26" in p:
            data_trovata = p
            break

    if not data_trovata:
        continue

    try:
        giorno, mese_txt, anno = data_trovata.split("-")

        mese = mesi.get(mese_txt[:3])
        if not mese:
            continue

        data_evento = datetime.strptime(f"{giorno}/{mese}/20{anno}", "%d/%m/%Y")

        # ✅ pulizia titolo
        titolo_pulito = riga.strip()
        titolo_pulito = titolo_pulito[:80]

        # ✅ trova città (tra parentesi tipo FI)
        luogo = ""
        match = re.search(r"\((.*?)\)", riga)
        if match:
            luogo = match.group(1)

        evento = Event()
        evento.name = titolo_pulito
        evento.begin = data_evento
        evento.make_all_day()
        evento.location = luogo

        calendar.events.add(evento)
        conteggio += 1

    except:
        continue

# ✅ salva calendario
os.makedirs("docs", exist_ok=True)

with open("docs/calendario_toscana.ics", "w", encoding="utf-8") as f:
    f.writelines(calendar)

print(f"✅ Creati {conteggio} eventi da PDF")
