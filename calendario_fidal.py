import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import re

ANNO = "2026"
# URL Corretto al 100%: Forziamo l'anno intero (anno=2026) e chiediamo tutti i mesi (mese=99)
url = "https://fidal.it"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    print("Connessione ai server FIDAL Toscana...")
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    calendar = Calendar()
    
    PAROLE_GIOVANILI = ["ragazzi", "ragazze", "cadetti", "cadette", "esordienti", "eso", "allievi", "allieve", "juniores", "u20", "u16", "u14", "coni", "giovanili", "provinciali"]
    
    righe = soup.find_all('tr')
    conteggio_totale = 0
    
    for riga in righe:
        testo_riga = riga.get_text(" | ", strip=True)
        if "|" in testo_riga:
            parti = [p.strip() for p in testo_riga.split("|")]
            
            if len(parti) >= 3:
                data_grezza = parti[0]
                titolo = parti[2]
                
                # Cerchiamo tipologia e luogo nelle colonne successive
                tipo_gara = ""
                luogo = ""
                for parte in parti[3:]:
                    if parte.upper() in ["PISTA", "INDOOR", "STRADA", "CROSS", "TRAIL"]:
                        tipo_gara = parte.upper()
                    elif "(" in parte and ")" in parte:
                        luogo = parte

                titolo_lower = titolo.lower()
                is_giovanile = any(cat in titolo_lower for cat in PAROLE_GIOVANILI)
                
                # Filtro: teniamo pista/indoor regionali e qualsiasi gara giovanile (anche provinciale)
                if (tipo_gara in ["PISTA", "INDOOR"]) or is_giovanile:
                    
                    # Eliminiamo gare senior su strada non giovanili
                    if any(x in tipo_gara.lower() for x in ["strada", "trail", "maratona"]) and not is_giovanile:
                        continue
                        
                    try:
                        # Gestione range di date es. "12-13/09" -> isoliamo "12/09"
                        giorno_mese = data_grezza
                        if "-" in giorno_mese:
                            parti_data = giorno_mese.split("-")
                            # Se la struttura è del tipo 12-13/09
                            if "/" in parti_data[1]:
                                mese = parti_data[1].split("/")[1]
                                giorno_mese = f"{parti_data[0]}/{mese}"
                        
                        # Generazione data finale pulita
                        data_pulita = f"{giorno_mese}/{ANNO}"
                        # Rimuove eventuali spazi o residui
                        data_pulita = re.sub(r'[^\d/]', '', data_pulita) 
                        
                        # Controlliamo la validità della stringa data (es. deve avere due barre)
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
                    except Exception as e:
                        continue

    with open('calendario_toscana.ics', 'w', encoding='utf-8') as f:
        f.writelines(calendar)
        
    print(f"\n[SUCCESSO] Il database completo è pronto!")
    print(f"Gare giovanili e su pista/indoor totali salvate: {conteggio_totale}")

except Exception as e:
    print(f"Errore generale: {e}")

