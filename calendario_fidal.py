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
# CALENDARIO
# ==========================

calendar = Calendar()
eventi_creati = 0
eventi_gia_inseriti = set()

# ==========================
# LETTURA FIDAL
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

        celle = riga.find_all("td")

        # la tabella FIDAL deve avere almeno 5 colonne
        if len(celle) < 5:
            continue

        try:

            data_testo = celle[0].get_text(" ", strip=True)
            livello = celle[1].get_text(" ", strip=True)
            denominazione = celle[2].get_text(" ", strip=True)
            tipologia = celle[3].get_text(" ", strip=True)
            localita = celle[4].get_text(" ", strip=True)

            testo_controllo = (
                f"{denominazione} {tipologia} {localita}"
            ).lower()

            # filtro categorie giovanili
            if not any(cat in testo_controllo for cat in PAROLE_GIOVANILI):
                continue

            # escludi master
            if any(exc in testo_controllo for exc in ESCLUSIONI):
                continue

            # estrae data tipo 11/04 oppure 12-13/09
            match = re.match(r"(\d{2})", data_testo)

            if not match:
                continue

            giorno = int(match.group(1))

            data_evento = datetime(
                ANNO,
                mese,
                giorno
            )

            # titolo più professionale
            titolo = denominazione.strip()

            if tipologia:
                titolo = f"{titolo} [{tipologia}]"

            chiave = (
                data_evento.strftime("%Y-%m-%d"),
                titolo
            )

            if chiave in eventi_gia_inseriti:
                continue

            eventi_gia_inseriti.add(chiave)

            evento = Event()
            evento.name = titolo
            evento.begin = data_evento
            evento.make_all_day()

            if localita:
                evento.location = localita

            calendar.events.add(evento)

            eventi_creati += 1

        except Exception:
            continue

# ==========================
# SALVATAGGIO
# ==========================

os.makedirs("docs", exist_ok=True)

with open(
    "docs/calendario_toscana.ics",
    "w",
    encoding="utf-8"
) as f:
    f.writelines(calendar)

print("")
print(f"✅ Eventi creati: {eventi_creati}")
