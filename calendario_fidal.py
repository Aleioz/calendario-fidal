import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import re
import time
import os

ANNO = "2026"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
calendar = Calendar()
conteggio_totale = 0

PAROLE_GIOVANILI = ["ragazzi", "ragazze", "cadetti", "cadette", "esordienti", "eso", "allievi", "allieve", "juniores", "u20", "u16", "u14", "coni", "giovanili", "provinciali"]

for mese_num in range(1, 13):
    url = f"https://fidal.it{ANNO}&mese={mese_num}"
    print(f"Scraping mese {mese_num}...")
    
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
                        if "-" in data_grezza:
                            parti_data = data_grezza.split("-")
                            if "/" in parti_data[1]:
                                mese_estratto = parti_data[1].split("/")[1]
                                data_grezza = f"{parti_data[0]}/{mese_estratto}"
                        
                        data_pulita = f"{data_grezza}/{ANNO}"
                        data_pulita = re.sub(r'[^\d/]', '', data_pulita)
                        
                        if data_pulita.count('/') == 2:
                            data_evento = datetime.strptime(data_pulita, "%d/%m/%Y")
                            
                            event = Event()
                            event.name = f"[{tipo_gara if tipo_gara else 'GARA'}] {titolo}"
                            event.begin = data_evento
                            if luogo:
                                event.location = luogo
                            event.make_all_day()
                            calendar.events.add(event)
                            conteggio_totale += 1
                    except:
                        continue
        time.sleep(1)
    except Exception as e:
        print(f"Errore temporaneo di rete sul mese {mese_num}: {e}")

# CONTROLLO BLOCCO DI SICUREZZA: Salva il file solo se ha trovato gare reali sul sito
if conteggio_totale > 0:
    with open('calendario_toscana.ics', 'w', encoding='utf-8') as f:
        f.writelines(calendar)
    print(f"\n[SUCCESSO] Calendario aggiornato con {conteggio_totale} gare!")
else:
    print("\n[ATTENZIONE] Il sito FIDAL ha restituito 0 gare. Blocco l'aggiornamento per non svuotare il calendario esistente.")
    # Se il file non esiste proprio (primo avvio), ne creiamo uno vuoto temporaneo per non far fallire GitHub
    if not os.path.exists('calendario_toscana.ics'):
        with open('calendario_toscana.ics', 'w', encoding='utf-8') as f:
            f.writelines(calendar)

