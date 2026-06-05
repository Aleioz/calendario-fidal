import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import re
import time
import os

# Calcola l'anno corrente in automatico in base alla data di oggi
ANNO_CORRENTE = str(datetime.now().year)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
calendar = Calendar()
conteggio_totale = 0

PAROLE_GIOVANILI = ["ragazzi", "ragazze", "cadetti", "cadette", "esordienti", "eso", "allievi", "allieve", "juniores", "u20", "u16", "u14", "coni", "giovanili", "provinciali", "rag"]

print(f"Avvio estrazione gare per l'anno {ANNO_CORRENTE}...")

# Controlliamo tutti i 12 mesi
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
                
                # Accettiamo gare su pista, indoor o qualunque cosa contenga parole giovanili
                if (tipo_gara in ["PISTA", "INDOOR"]) or is_giovanile:
                    if any(x in tipo_gara.lower() for x in ["strada", "trail", "maratona"]) and not is_giovanile:
                        continue
                        
                    if not data_grezza or "/" not in data_grezza:
                        continue
                        
                    try:
                        # Gestione dei giorni doppi (es: 14-15/06 prende il 14)
                        if "-" in data_grezza:
                            data_grezza = data_grezza.split("-")[0] + "/" + data_grezza.split("/")[-1]
                        
                        # Costruiamo la data finale pulita
                        data_pulita = f"{data_grezza}/{ANNO_CORRENTE}"
                        data_pulita = re.sub(r'[^\d/]', '', data_pulita)
                        
                        # Se l'anno è rimasto scritto a due cifre (es. 15/06/25), correggiamo in 2025
                        if data_pulita.count('/') == 2:
                            parti_data = data_pulita.split('/')
                            if len(parti_data[2]) == 2:
                                data_pulita = f"{parti_data[0]}/{parti_data[1]}/20{parti_data[2]}"
                                
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
        time.sleep(0.5)
    except Exception as e:
        print(f"Errore mese {mese_num}: {e}")

# Salvataggio protetto: scrive il file solo se ha catturato eventi reali
if conteggio_totale > 0:
    with open('calendario_toscana.ics', 'w', encoding='utf-8') as f:
        f.writelines(calendar)
    print(f"\n[SUCCESSO] Estratte {conteggio_totale} gare della Toscana!")
else:
    print("\n[ERRORE] Il server FIDAL non ha restituito gare. Controllo filtri.")
    # Crea un file minimo di test per non bloccare l'esecuzione di GitHub
    with open('calendario_toscana.ics', 'w', encoding='utf-8') as f:
        f.writelines(calendar)

