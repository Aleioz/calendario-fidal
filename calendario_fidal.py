import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import os

calendar = Calendar()
conteggio = 0

url = "https://www.fidal.it/calendario.php"

headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# ✅ trova tutte le righe
righe = soup.find_all("tr")

for riga in righe:
    colonne = riga.find_all("td")

    if len(colonne) >= 4:
        try:
            data = colonne[0].text.strip()
            titolo = colonne[2].text.strip().lower()
            luogo = colonne[4].text.strip() if len(colonne) > 4 else ""

            # ✅ FILTRO GIOVANILI
            if not any(x in titolo for x in ["ragazzi", "cadetti", "allievi", "juniores", "esordienti"]):
                continue

            # ✅ FILTRO TOSCANA (puoi adattarlo meglio)
            if "tosc" not in luogo.lower():
                continue

            if "/" not in data:
                continue

            data_evento = datetime.strptime(data + "/2026", "%d/%m/%Y")

            evento = Event()
            evento.name = titolo
            evento.begin = data_evento
            evento.make_all_day()
            evento.location = luogo

            calendar.events.add(evento)
            conteggio += 1

        except:
            continue

# ✅ salva
os.makedirs("docs", exist_ok=True)

with open("docs/calendario_toscana.ics", "w", encoding="utf-8") as f:
    f.writelines(calendar)

print(f"✅ Creati {conteggio} eventi automatici")
