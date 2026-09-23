import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import os
import re

calendar = Calendar()

ANNO = 2026

PAROLE_GIOVANILI = [
    "esordienti",
    "ragazzi",
    "ragazze",
    "cadetti",
    "cadette",
    "allievi",
    "allieve",
    "juniores"
]

ESCLUSIONI = [
    "master"
]

eventi_creati = 0

for mese in range(1, 13):

    url = f"https://www.fidal.it/calendario.php?&id_sito=126&submit=Invia&livello=REG&new_regione=TOSCANA&anno={ANNO}&mese={mese}"

    print("Leggo:", url)

    html = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    ).text

    soup = BeautifulSoup(html, "html.parser")

    righe = soup.find_all("tr")

    print("Righe trovate:", len(righe))

    for riga in righe:

        testo = riga.get_text(" ", strip=True)

        if not testo:
            continue

        testo_lower = testo.lower()

        if not any(x in testo_lower for x in PAROLE_GIOVANILI):
            continue

        if any(x in testo_lower for x in ESCLUSIONI):
            continue

        match = re.match(r"(\d{2})/(\d{2})", testo)

        if not match:
            continue

        try:

            giorno = int(match.group(1))
            mese_evento = int(match.group(2))

            data_evento = datetime(
                ANNO,
                mese_evento,
                giorno
            )

            evento = Event()
            evento.name = testo[:120]
            evento.begin = data_evento
            evento.make_all_day()

            calendar.events.add(evento)

            eventi_creati += 1

        except Exception:
            continue

os.makedirs("docs", exist_ok=True)

with open(
    "docs/calendario_toscana.ics",
    "w",
    encoding="utf-8"
) as f:
    f.writelines(calendar)

print("Eventi creati:", eventi_creati)
