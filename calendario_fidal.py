import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import re
import time

ANNO_CORRENTE = str(datetime.now().year)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
calendar = Calendar()
conteggio_totale = 0

PAROLE_GIOVANILI = ["ragazzi", "ragazze", "cadetti", "cadette", "esordienti", "eso", "allievi", "allieve", "juniores", "u20", "u16", "u14", "coni", "giovanili", "provinciali", "rag"]

print(f"Avvio estrazione gare per l'anno {ANNO_CORRENTE}...")

for mese_num in range(1, 13):
    url = f"https://fidal.it{ANNO_CORRENTE}&mese={mese_num}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        righe = soup.find_all('tr')
        for riga in righe:
            colonne = riga.find_all('td')
            if len(colonne) >= 3:
                data_grezza = colonne[0].text.strip()
                titolo = colonne[2].text.strip()
                
                tipo_gara = ""
                luogo = ""
                for col in colonne[3:]:
                    txt = col.text.strip().upper()
                    if txt in ["PISTA", "INDOOR", "STRADA", "CROSS", "TRAIL"]:
                        tipo_gara = txt
                    elif "(" in txt and ")" in txt:
                        luogo = col.text.strip()

                titolo_lower = titolo.lower()
                is_giovanile = any(cat in titolo_lower for cat in PAROLE_GIOVANILI)
                
                if (tipo_gara in ["PISTA", "INDOOR"]) or is_giovanile:
                    if any(x in tipo_gara.lower() for x in ["strada", "trail", "maratona"]) and not is_giovanile:
                        continue
                        
                    if not data_grezza or "/" not in data_grezza:
                        continue
                        
                    try:
                        # Gestione intervalli di date (es. 14-15/06 -> prende il 14/06)
                        if "-" in data_grezza:
                            parti_trattino = data_grezza.split("-")
                            if "/" in parti_trattino[0]:
                                data_grezza = parti_trattino[0]
                            elif "/" in parti_trattino[1]:
                                mese_estratto = parti_trattino[1].split("/")[-1]
                                data_grezza = f"{parti_trattino[0]}/{mese_estratto}"
                        
                        # Costruzione della data finale pulita giorno/mese/anno
                        parti_barra = data_grezza.split("/")
                        giorno = int(parti_barra[0])
                        mese = int(parti_barra[1])
                        
                        data_pulita = f"{giorno:02d}/{mese:02d}/{ANNO_CORRENTE}"
                        data_evento = datetime.strptime(data_pulita, "%d/%m/%Y")
                        
                        event = Event()
                        event.name = f"[{tipo_gara if tipo_gara else 'GARA'}] {titolo}"
                        event.begin = data_evento
                        if luogo:
                            event.location = luogo
                        event.make_all_day()
                        calendar.events.add(event)
                        conteggio_totale += 1
                    except Exception as e:
                        continue
        time.sleep(0.3)
    except Exception as e:
        print(f"Errore mese {mese_num}: {e}")

# Scrive sempre il file per aggiornare Google Calendar
with open('calendario_toscana.ics', 'w', encoding='utf-8') as f:
    f.writelines(calendar)

print(f"\n[SUCCESSO] Il file contiene {conteggio_totale} gare della Toscana per il {ANNO_CORRENTE}!")

