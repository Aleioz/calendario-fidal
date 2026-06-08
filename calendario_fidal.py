from pypdf import PdfReader
from ics import Calendar, Event
from datetime import datetime
import os

calendar = Calendar()
conteggio = 0

# ✅ leggi PDF
reader = PdfReader("calendario estivo.pdf")

testo = ""
for pagina in reader.pages:
    testo += pagina.extract_text() + "\n"

righe = testo.split("\n")

# ✅ categorie GIUSTE
CATEGORIE_OK = ["ragazzi", "cadetti", "allievi", "juniores", "esordienti"]

# ✅ città Toscana (chiave per filtro serio)
CITTA_TOSCANA = [
    "firenze","prato","pistoia","arezzo","siena",
    "lucca","pisa","livorno","massa","grosseto",
    "empoli","carrara","monsummano","grosseto"
]

# ✅ mesi
mesi = {
    "gen": "01","feb": "02","mar": "03","apr": "04","mag": "05","giu": "06",
    "lug": "07","ago": "08","set": "09","ott": "10","nov": "11","dic": "12"
}

for riga in righe:

    riga_lower = riga.lower()

    # ✅ 1. filtro categorie giovanili
    if not any(cat in riga_lower for cat in CATEGORIE_OK):
        continue

    # ✅ 2. filtro regione Toscana (basato su città)
    if not any(citta in riga_lower for citta in CITTA_TOSCANA):
        continue

    # ✅ 3. escludi gare inutili
    if "master" in riga_lower:
        continue
    if "internaz" in riga_lower:
        continue

    # ✅ trova data (es: 15-mar-26)
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

        # ✅ estrai città
        luogo = ""
        for parola in parti:
            if parola.lower() in CITTA_TOSCANA:
                luogo = parola.title()
                break

        # ✅ titolo professionale
        # togli parte iniziale (data + giorno)
        titolo = " ".join(parti[2:])

        # pulizia parole inutili
        titolo = titolo.replace("reg.le", "").replace("pista", "Pista")
        titolo = titolo.replace("strada", "Strada")

        # accorcia titolo
        if len(titolo) > 70:
            titolo = titolo[:70]

        # aggiungi città nel titolo
        if luogo:
            titolo = f"{titolo} – {luogo}"

        # ✅ crea evento
        evento = Event()
        evento.name = titolo.strip()
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

print(f"✅ Creati {conteggio} eventi filtrati PRO")
