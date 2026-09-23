import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import os
import re

# ==========================================
# CONFIGURAZIONE
# ==========================================

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

# ==========================================
# INIZIALIZZAZIONE
# ==========================================

calendar = Calendar()
eventi_creati = 0
eventi_gia_inseriti = set()

# ==========================================
# LETTURA CALENDARIO FIDAL
# ==========================================

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
        if not any(cat in testo_lower for cat in PAROLE_GIOVANILI):
            continue

        # escludi master
        if any(exc in testo_lower for exc in ESCLUSIONI):
            continue

        # ricerca data iniziale tipo 17/01
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

            # elimina data e livello "R"
            parti = testo.split()

            if len(parti) > 2:
                titolo = " ".join(parti[2:])
            else:
                titolo = testo

            titolo = titolo.strip()

            # ==========================
            # ESTRAZIONE LOCALITA'
            # ==========================

            localita = ""

            match_localita = re.search(
                r"([A-Za-zÀ-ÿ\s'\-]+)\s+\([A-Z]{2}\)$",
                titolo
            )

            if match_localita:

                localita = match_localita.group(1).strip()

                titolo = titolo.replace(
                    match_localita.group(0),
                    ""
                ).strip()

            titolo = re.sub(r"\s+", " ", titolo)

            # ==========================
            # ELIMINAZIONE DUPLICATI
            # ==========================

            chiave = (
                data_evento.strftime("%Y-%m-%d"),
                titolo
            )

            if chiave in eventi_gia_inseriti:
                continue

            eventi_gia_inseriti.add(chiave)

            # ==========================
            # CREAZIONE EVENTO
            # ==========================

            evento = Event()

            evento.name = titolo[:150]
            evento.begin = data_evento
            evento.make_all_day()

            if localita:
                evento.location = localita

            calendar.events.add(evento)

            eventi_creati += 1

        except Exception:
            continue

# ==========================================
# SALVATAGGIO FILE
# ==========================================

os.makedirs("docs", exist_ok=True)

with open(
    "docs/calendario_toscana.ics",
    "w",
    encoding="utf-8"
) as f:
    f.writelines(calendar)

print()
print(f"✅ Eventi creati: {eventi_creati}")
