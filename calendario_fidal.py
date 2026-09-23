import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import os
import re

# ==========================
# CONFIGURAZIONE
# ==========================

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

# ==========================
# CREAZIONE CALENDARIO
# ==========================

calendar = Calendar()
eventi_creati = 0

# Per evitare duplicati
eventi_gia_inseriti = set()

# ==========================
# LETTURA CALENDARIO FIDAL
# ==========================

for mese in range(1, 13):

    url = (
        f"https://www.fidal.it/calendario.php?"
        f"&id_sito=126"
        f"&submit=Invia"
        f"&livello=REG"
        f"&new_regione=TOSCANA"
        f"&anno={ANNO}"
        f"&mese={mese}"
    )

    print(f"Leggo mese {mese}...")

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    soup = BeautifulSoup(response.text, "html.parser")

    righe = soup.find_all("tr")

    print(f"Righe trovate: {len(righe)}")

    for riga in righe:

        testo = riga.get_text(" ", strip=True)

        if not testo:
            continue

        testo_lower = testo.lower()

        # filtro categorie giovanili
        if not any(x in testo_lower for x in PAROLE_GIOVANILI):
            continue

        # escludi master
        if any(x in testo_lower for x in ESCLUSIONI):
            continue

        # cerca data iniziale tipo 17/01
        match_data = re.match(r"(\d{2})/(\d{2})", testo)

        if not match_data:
            continue

        try:

            giorno = int(match_data.group(1))
            mese_evento = int(match_data.group(2))

            data_evento = datetime(
                ANNO,
                mese_evento,
                giorno
            )

            # titolo pulito
            parti = testo.split()

            if len(parti) > 2:
                titolo = " ".join(parti[2:])
            else:
                titolo = testo

            titolo = titolo.strip()

            # elimina duplicati
            chiave = (
                data_evento.strftime("%Y-%m-%d"),
                titolo
            )

            if chiave in eventi_gia_inseriti:
                continue

            eventi_gia_inseriti.add(chiave)

            evento = Event()
            evento.name = titolo[:150]
            evento.begin = data_evento
            evento.make_all_day()

            calendar.events.add(evento)

            eventi_creati += 1

        except Exception:
            continue

# ==========================
# SALVATAGGIO FILE
# ==========================

os.makedirs("docs", exist_ok=True)

with open(
    "docs/calendario_toscana.ics",
    "w",
    encoding="utf-8"
) as f:
    f.writelines(calendar)

print()
print(f"✅ Eventi creati: {eventi_creati}")
