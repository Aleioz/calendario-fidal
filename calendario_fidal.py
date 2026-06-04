import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import re

ANNO = "2026"
url = "https://www.fidal.it/calendario.php?&id_sito=126&submit=Invia&livello=REG&new_regione=TOSCANA&anno=99&mese=99"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    print("Connessione al server FIDAL Toscana...")
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    calendar = Calendar()
    
    PAROLE_GIOVANILI = ["ragazzi", "ragazze", "cadetti", "cadette", "esordienti", "eso", "allievi", "allieve", "juniores", "u20", "u16", "u14", "coni", "giovanili"]
    mesi_mappa = {"gen": "01", "feb": "02", "mar": "03", "apr": "04", "mag": "05", "giu": "06", "lug": "07", "ago": "08", "set": "09", "ott": "10", "nov": "11", "dic": "12"}
    
    righe = soup.find_all('tr')
    conteggio_totale = 0
    
    for riga in righe:
        testo_riga = riga.get_text(" | ", strip=True)
        if "|" in testo_riga:
            parti = [p.strip() for p in testo_riga.split("|")]
            
            if len(parti) >= 3:
                data_grezza = parti[0]
                titolo = parti[2]
                
                tipo_gara = ""
                luogo = ""
                for parte in parti[3:]:
                    if parte.upper() in ["PISTA", "INDOOR", "STRADA", "CROSS", "TRAIL"]:
                        tipo_gara = parte.upper()
                    elif "(" in parte and ")" in parte:
                        luogo = parte

                titolo_lower = titolo.lower()
                is_giovanile = any(cat in titolo_lower for cat in PAROLE_GIOVANILI)
                
                if (tipo_gara in ["PISTA", "INDOOR"]) or is_giovanile:
                    try:
                        # Gestione dei range di date (es: 12-13/09 prende il 12)
                        giorno_mese = data_grezza.split("-")[0] if "-" in data_grezza else data_grezza
                        
                        giorno = "01"
                        mese = "01"
                        
                        # Caso 1: Formato classico con numeri (es: 16/06 o 16/06/26)
                        if "/" in giorno_mese:
                            componenti = giorno_mese.split("/")
                            giorno = componenti[0]
                            mese = componenti[1]
                        # Caso 2: Formato testuale (es: 13-set-26 o 13-set)
                        else:
                            match_num = re.search(r'\d+', giorno_mese)
                            if match_num:
                                giorno = match_num.group()
                            for k, v in mesi_mappa.items():
                                if k in giorno_mese.lower():
                                    mese = v
                                    break
                        
                        # Pulizia finale dei numeri
                        data_pulita = f"{int(giorno):02d}/{int(mese):02d}/{ANNO}"
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
        
    print(f"\n[SUCCESSO] Calendario aggiornato con {conteggio_totale} gare!")

except Exception as e:
    print(f"Errore: {e}")

