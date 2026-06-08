from pypdf import PdfReader
from ics import Calendar, Event
from datetime import datetime
import os
import re

calendar = Calendar()
conteggio = 0

reader = PdfReader("calendario estivo.pdf")

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

    # ✅ filtro categorie giovanili
    if not any(cat in riga_lower for cat in CATEGORIE_OK):
        continue

    # ✅ escludi roba inutile
    if "master" in riga_lower or "internaz" in riga_lower:
        continue

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

        # ✅ TROVA CITTÀ (prima parola tutta maiuscola dopo la data)
        luogo = ""
        for p in parti:
            if p.isupper() and len(p) > 3:
                luogo = p.title()
                break

        # ✅ CREA TITOLO PROFESSIONALE

        testo_pulito = " ".join(parti[3:])

        # pulizia parole inutili
        testo_pulito = re.sub(r"\b(reg\.le|inter\.le|naz\.le)\b", "", testo_pulito, flags=re.IGNORECASE)
        testo_pulito = testo_pulito.replace("  ", " ")

        # riduci lunghezza
        testo_pulito = testo_pulito.strip()[:70]

        # titolo finale
        if luogo:
            titolo = f"{testo_pulito} – {luogo}"
        else:
            titolo = testo_pulito

        evento = Event()
        evento.name = titolo
        evento.begin = data_evento
        evento.make_all_day()
        evento.location = luogo

        calendar.events.add(evento)
        conteggio += 1

    except:
        continue

os.makedirs("docs", exist_ok=True)

with open("docs/calendario_toscana.ics", "w", encoding="utf-8") as f:
    f.writelines(calendar)

print(f"✅ Creati {conteggio} eventi professionali")
