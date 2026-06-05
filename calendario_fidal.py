import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import re
import time

# Usiamo l'anno corrente in automatico
ANNO_CORRENTE = str(datetime.now().year)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
calendar = Calendar()
conteggio_totale = 0

# Parole chiave per intercettare le categorie che ti interessano
PAROLE_GIOVANILI = ["ragazzi", "ragazze", "cadetti", "cadette", "esordienti", "eso", "allievi", "allieve", "juniores", "u20", "u16", "u14", "coni", "giovanili", "provinciali", "rag"]

print(f"Inizio estrazione gare FIDAL Toscana per l'anno {ANNO_CORRENTE}...")

for mese_num in range(1, 13):
    # Interroghiamo i mesi uno ad uno
    url = f"https://fidal.it{ANNO_CORRENTE}&mese={mese_num}"
    print(f"Controllo mese {mese_num}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Troviamo tutte le righe della tabella del sito
        righe = soup.find_all('tr')
        for riga in righe:
            colonne = riga.find_all('td')
            if len(colonne) >= 3:
                data_grezza = colonne[0].text.strip()
                titolo = colonne[2].text.strip()
                
                # Cerca la tipologia e il luogo se presenti
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
                
                # Se la gara è su pista/indoor o se contiene parole giovanili, la teniamo
                if (tipo_gara in ["PISTA", "INDOOR"]) or is_giovanile:
                    # Salta le gare senior su strada
                    if any(x in tipo_gara.lower() for x in ["strada", "trail", "maratona"]) and not is_giovanile:
                        continue
                        
                    if not data_grezza or "/" not in data_grezza:
                        continue
                        
                    try:
                        # Gestione dei giorni doppi (es. 14-15/06 -> prende il 14/06)
                        if "-" in data_grezza:
                            data_grezza = data_grezza.split("-")[0] + "/" + data_grezza.split("/")[-1]
                        
                        # Estraiamo giorno e mese puliti
                        parti_barra = data_grezza.split("/")
                        giorno = int(re.sub(r'[^\d]', '', parti_barra[0]))
                        mese = int(re.sub(r'[^\d]', '', parti_barra[1]))
                        
                        # Costruiamo la data finale
                        data_pulita = f"{giorno:02d}/{mese:02d}/{ANNO_CORRENTE}"
                        data_evento = datetime.strptime(data_pulita, "%d/%m/%Y")
                        
                        # Generiamo l'evento
                        event = Event()
                        event.name = f"[{tipo_gara if tipo_gara else 'GARA'}] {titolo}"
                        event.begin = data_evento
                        if luogo := luogo:
                            event.location = luogo
                        event.make_all_day()
                        calendar.events.add(event)
                        conteggio_totale += 1
                    except:
                        continue
        # Pausa di mezzo secondo tra le richieste per non farsi bloccare dalla FIDAL
        time.sleep(0.5)
    except Exception as e:
        print(f"Errore durante il controllo del mese {mese_num}: {e}")

# Sovrascriviamo il file per aggiornare internet
with open('calendario_toscana.ics', 'w', encoding='utf-8') as f:
    f.write(calendar.serialize())

print(f"\n[SUCCESSO] Il file calendario_toscana.ics è stato salvato con {conteggio_totale} gare!")
