import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime

headers = {'User-Agent': 'Mozilla/5.0'}
calendar = Calendar()
conteggio_totale = 0

urls = [
    "https://www.fidal.it/calendario.php"
]

PAROLE_GIOVANILI = ["ragazzi", "ragazze", "cadetti", "cadette", "esordienti", "eso", "allievi", "allieve", "juniores", "giovanili"]
ESCLUSIONI = ["master", "assoluti", "promesse"]

print("Avvio estrazione dati...")

for url in urls:
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        righe = soup.find_all('tr')

        for riga in righe:
            colonne = riga.find_all('td')

            if len(colonne) >= 4:

                testi_celle = [c.get_text().strip() for c in colonne]

                try:
                    data_testo = testi_celle.pop(0)
                    livello = testi_celle.pop(0)
                    titolo = testi_celle.pop(0)
                    tipo_gara = testi_celle.pop(0).lower()
                    luogo = testi_celle.pop(0) if testi_celle else ""

                    # filtro strada
                    if any(x in tipo_gara for x in ["strada", "trail", "montagna"]):
                        continue

                    titolo_lower = titolo.lower()

                    if any(esc in titolo_lower for esc in ESCLUSIONI) and not any(cat in titolo_lower for cat in PAROLE_GIOVANILI):
                        continue

                    if "/" not in data_testo:
                        continue

                    # gestione date
                    if "-" in data_testo:
                        giorno = data_testo.split("-")[0]
                        mese = data_testo.split("/")[-1]
                        data_pulita = f"{giorno}/{mese}/2026"
                    else:
                        data_pulita = data_testo + "/2026"

                    data_evento = datetime.strptime(data_pulita, "%d/%m/%Y")

                    event = Event()
                    event.name = f"[{tipo_gara.upper()}] {titolo}"
                    event.begin = data_evento
                    event.end = data_evento
                    event.location = luogo

                    calendar.events.add(event)
                    conteggio_totale += 1

                except Exception as e:
                    continue

    except Exception as e:
        print(f"Errore rete: {e}")

import os

# crea la cartella docs se non esiste
os.makedirs("docs", exist_ok=True)

# salva il file dentro docs
with open("docs/calendario_fidal.ics", "w", encoding="utf-8") as f:
    f.writelines(calendar)

print(f"\n✅ Creato file docs/calendario_fidal.ics con {conteggio_totale} eventi")

