from pypdf import PdfReader
from ics import Calendar, Event
from datetime import datetime
import os
import re

calendar = Calendar()
conteggio = 0

# ✅ apre PDF (assicurati che sia nel repo)
reader = PdfReader("BOZZA calendario estivo Toscana 2026.pdf")

testo = ""

# ✅ estrai testo da tutte le pagine
for pagina in reader.pages:
    testo += pagina.extract_text() + "\n"

# ✅ divide in righe
righe = testo.split("\n")

# ✅ categorie giovanili
CATEGORIE_OK = ["ragazzi", "cadetti", "allievi", "juniores", "esordienti"]

for riga in righe:
    try:
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

        giorno, mese_txt, anno = data_trovata.split("-")

        mesi = {
            "gen": "01","feb": "02","mar": "03","apr": "04","mag": "05","giu": "06",
            "lug": "07","ago": "08","set": "09","ott": "10","nov": "11","dic": "12"
        }

        mese = mesi.get(mese_txt[:3])
        if not mese:
            continue

        data_evento = datetime.strptime(f"{giorno}/{mese}/20{anno}", "%d/%m/%Y")

