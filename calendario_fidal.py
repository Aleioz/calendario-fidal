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
 
mesi_trovati = 0
 
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
 
# filtro giovanili
if not any(x in testo_lower for x in PAROLE_GIOVANILI):
continue
 
# escludi master
if any(x in testo_lower for x in ESCLUSIONI):
continue
 
# cerca data
data_match = re.match(r"(\d{2})/(\d{2})", testo)
 
if not data_match:
continue
 
try:
 
giorno = int(data_match.group(1))
mese_num = int(data_match.group(2))
 
data_evento = datetime(
ANNO,
mese_num,
giorno
)
 
evento = Event()
 
evento.name = testo[:120]
 
evento.begin = data_evento
 
evento.make_all_day()
 
calendar.events.add(evento)
 
mesi_trovati += 1
 
except:
continue
 
os.makedirs("docs", exist_ok=True)
 
with open(
"docs/calendario_toscana.ics",
"w",
encoding="utf-8"
) as f:
f.writelines(calendar)
 
print("Eventi creati:", mesi_trovati)
