from pypdf import PdfReader
from ics import Calendar, Event
from datetime import datetime
import os

calendar = Calendar()
conteggio = 0

# ✅ apri PDF
reader = PdfReader("calendario estivo.pdf")

# ✅ estrai tutto il testo
testo = ""

for pagina in reader.pages:
    testo += pagina.extract_text() + "\n"

# ✅ stampa parte testo per debug
print(testo[:2000])

# ✅ SPLIT per righe
righe = testo.split("\n")

for riga in righe:
    try:
        riga_lower = riga.lower()

        # filtro minimo (giovanili)
        if not any(x in riga_lower for x in ["ragazzi", "cadetti", "allievi", "juniores", "esordienti"]):
            continue

        # cerca una data base (es: 12-apr-26)
        parti = riga.split()

        data_trovata = None
        for p in parti:
            if "-" in p and "26" in p:
                data_trovata = p
                break

        if not data_trovata:
            continue

        # esempio: 12-apr-26
        giorno, mese_txt, anno = data_trovata.split("-")

        mesi = {
            "gen": "01","feb": "02","mar": "03","apr": "04","mag": "05","giu": "06",
            "lug": "07","ago": "08","set": "09","ott": "10","nov": "11","dic": "12"
        }

        mese = mesi.get(mese_txt[:3])
        if not mese:
            continue

        data_evento = datetime.strptime(f"{giorno}/{mese}/20{anno}", "%d/%m/%Y")

        # crea evento base
        evento = Event()
        evento.name = riga[:100]   # nome ridotto
        evento.begin = data_evento
        evento.make_all_day()

        calendar.events.add(evento)
        conteggio += 1

    except:
        continue

# ✅ salva calendario
os.makedirs("docs", exist_ok=True)

with open("docs/calendario_toscana.ics", "w", encoding="utf-8") as f:
    f.writelines(calendar)

print(f"✅ Creati {conteggio} eventi base")
